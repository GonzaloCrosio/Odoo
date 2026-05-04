# -*- coding: utf-8 -*-

import logging
import re
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

MSGID_RE   = re.compile(r"<[^>]+>")
ALIAS_RE   = re.compile(r"[\w.+-]+@[\w.-]+")


def _extract_msgids(value: str):
    if not value:
        return []
    return MSGID_RE.findall(value)


def _extract_emails(value: str):
    if not value:
        return []
    return ALIAS_RE.findall(value.lower())


def _find_parent_message(env, in_reply_to: str, references: str):
    """
    Busca el mensaje padre probando TODOS los message_id candidatos
    en In-Reply-To y References, en orden de prioridad.
    """
    candidate_ids = []
    irt_ids = _extract_msgids(in_reply_to)
    candidate_ids += irt_ids
    ref_ids = _extract_msgids(references)
    candidate_ids += list(reversed(ref_ids))

    seen = set()
    unique_candidates = []
    for c in candidate_ids:
        if c not in seen:
            seen.add(c)
            unique_candidates.append(c)

    _logger.info("[INBOUND] Candidatos message_id a buscar: %s", unique_candidates)

    if not unique_candidates:
        return None

    parent = env["mail.message"].sudo().search(
        [("message_id", "in", unique_candidates)],
        order="id desc",
        limit=1,
    )

    if parent:
        _logger.info(
            "[INBOUND] Parent encontrado: id=%s message_id=%s model=%s res_id=%s",
            parent.id, parent.message_id, parent.model, parent.res_id,
        )
    else:
        _logger.warning(
            "[INBOUND] NINGÚN candidato encontrado en mail.message. Candidatos: %s",
            unique_candidates,
        )

    return parent or None


def _find_alias(env, email_address: str):
    if not email_address or "@" not in email_address:
        return None
    local_part = email_address.split("@")[0]
    alias = env["mail.alias"].sudo().search(
        [("alias_name", "=", local_part)],
        limit=1,
    )
    _logger.info("[INBOUND] Buscando alias '%s' → %s", local_part, alias)
    return alias or None


def _post_on_record(env, model_name, res_id, vals):
    try:
        record = env[model_name].sudo().browse(res_id)
        if not record.exists():
            _logger.warning("[INBOUND] Record %s(%s) no existe", model_name, res_id)
            return False
        record.message_post(
            body=vals.get("body", ""),
            subject=vals.get("subject", ""),
            message_type="comment",
            subtype_xmlid="mail.mt_comment",
            author_id=False,
            email_from=vals.get("email_from", ""),
            message_id=vals.get("message_id") or False,
        )
        _logger.info("[INBOUND] message_post OK en %s(%s)", model_name, res_id)
        return True
    except Exception as e:
        _logger.error("[INBOUND] Error en message_post %s(%s): %s", model_name, res_id, e, exc_info=True)
        return False


class MailInboundController(http.Controller):

    @http.route(
        "/mail/inbound",
        type="json",
        auth="public",
        methods=["POST"],
        csrf=False,
    )
    def mail_inbound(self, **payload):
        subject     = payload.get("subject") or "(sin asunto)"
        body        = payload.get("body") or ""
        email_from  = payload.get("from") or ""
        in_reply_to = payload.get("in_reply_to") or ""
        references  = payload.get("references") or ""
        msgid       = payload.get("message_id") or ""
        to_field    = payload.get("to") or ""
        cc_field    = payload.get("cc") or ""

        _logger.info(
            "[INBOUND] ══════════════════════════════════\n"
            "  from        = %r\n"
            "  to          = %r\n"
            "  subject     = %r\n"
            "  message_id  = %r\n"
            "  in_reply_to = %r\n"
            "  references  = %r",
            email_from, to_field, subject, msgid, in_reply_to, references,
        )

        env = request.env

        # ------------------------------------------------------------------ #
        # DIAGNÓSTICO: últimos message_ids enviados por Odoo                  #
        # ------------------------------------------------------------------ #
        recent_msgs = env["mail.message"].sudo().search(
            [("message_id", "!=", False), ("message_type", "in", ["email", "comment"])],
            order="id desc",
            limit=10,
        )
        _logger.info(
            "[INBOUND][DIAG] Últimos 10 message_ids en Odoo:\n%s",
            "\n".join(
                f"  id={m.id} model={m.model} res_id={m.res_id} msgid={m.message_id}"
                for m in recent_msgs
            ),
        )

        # ------------------------------------------------------------------ #
        # PASO 1: Buscar por In-Reply-To + References                         #
        # ------------------------------------------------------------------ #
        parent = _find_parent_message(env, in_reply_to, references)

        if parent and parent.model and parent.res_id:
            ok = _post_on_record(env, parent.model, parent.res_id, {
                "body": body, "subject": subject,
                "email_from": email_from, "message_id": msgid,
            })
            if ok:
                return {
                    "status": "ok", "linked": True,
                    "method": "parent_msgid",
                    "model": parent.model, "res_id": parent.res_id,
                }

        # ------------------------------------------------------------------ #
        # PASO 2: Buscar por alias en To: y CC:                               #
        # ------------------------------------------------------------------ #
        all_recipients = _extract_emails(to_field) + _extract_emails(cc_field)
        _logger.info("[INBOUND] Destinatarios para alias: %s", all_recipients)

        for email_addr in all_recipients:
            local = email_addr.split("@")[0] if "@" in email_addr else ""
            if local in ("catchall", "bounce", "notifications"):
                _logger.info("[INBOUND] Saltando alias reservado: %s", local)
                continue

            alias = _find_alias(env, email_addr)
            if not alias:
                continue

            alias_model  = alias.alias_model_id.model if alias.alias_model_id else None
            alias_res_id = alias.alias_force_thread_id or None

            if alias_model and alias_res_id:
                ok = _post_on_record(env, alias_model, alias_res_id, {
                    "body": body, "subject": subject,
                    "email_from": email_from, "message_id": msgid,
                })
                if ok:
                    return {
                        "status": "ok", "linked": True,
                        "method": "alias_forced_thread",
                        "model": alias_model, "res_id": alias_res_id,
                        "alias": alias.alias_name,
                    }

            if alias_model:
                try:
                    import ast
                    defaults = {}
                    if alias.alias_defaults:
                        try:
                            defaults = ast.literal_eval(alias.alias_defaults)
                        except Exception:
                            pass
                    Model = env[alias_model].sudo()
                    create_vals = {**defaults}
                    if "name" in Model._fields:
                        create_vals.setdefault("name", subject)
                    new_record = Model.create(create_vals)
                    new_record.message_post(
                        body=body, subject=subject,
                        message_type="comment",
                        subtype_xmlid="mail.mt_comment",
                        email_from=email_from,
                        message_id=msgid or False,
                    )
                    return {
                        "status": "ok", "linked": True,
                        "method": "alias_new_record",
                        "model": alias_model, "res_id": new_record.id,
                        "alias": alias.alias_name,
                    }
                except Exception as e:
                    _logger.error("[INBOUND] Error creando via alias %s: %s", alias.alias_name, e, exc_info=True)

        # ------------------------------------------------------------------ #
        # PASO 3: Fallback silencioso (nota interna, no notifica)             #
        # ------------------------------------------------------------------ #
        _logger.warning(
            "[INBOUND] FALLBACK — sin match. from=%r to=%r in_reply_to=%r",
            email_from, to_field, in_reply_to,
        )
        try:
            env["res.partner"].sudo().browse(1).message_post(
                body=(
                    f"<p><b>Correo sin enlazar</b></p>"
                    f"<p><b>De:</b> {email_from}</p>"
                    f"<p><b>Para:</b> {to_field}</p>"
                    f"<p><b>Asunto:</b> {subject}</p>"
                    f"<p><b>In-Reply-To:</b> {in_reply_to}</p>"
                    f"<p><b>References:</b> {references}</p>"
                    f"<hr/>{body}"
                ),
                subject=f"[SIN ENLAZAR] {subject}",
                message_type="comment",
                subtype_xmlid="mail.mt_note",
                email_from=email_from,
                message_id=msgid or False,
            )
        except Exception as e:
            _logger.error("[INBOUND] Error en fallback: %s", e, exc_info=True)

        return {"status": "ok", "linked": False, "method": "fallback"}