# -*- coding: utf-8 -*-
import re
from odoo import http
from odoo.http import request


MSGID_RE = re.compile(r"<[^>]+>")

def _extract_msgids(value: str):
    """Devuelve lista de Message-IDs con formato <...> encontrados en un string."""
    if not value:
        return []
    return MSGID_RE.findall(value)


class MailInboundController(http.Controller):

    @http.route("/mail/inbound", type="json", auth="public", methods=["POST"], csrf=False)
    def mail_inbound(self, **payload):
        subject = payload.get("subject") or "(sin asunto)"
        body = payload.get("body") or ""
        email_from = payload.get("from") or ""
        in_reply_to = payload.get("in_reply_to") or ""
        references = payload.get("references") or ""
        msgid = payload.get("message_id") or ""

        # 1) Intentar encontrar el mensaje padre por In-Reply-To y References
        candidate_ids = []
        candidate_ids += _extract_msgids(in_reply_to)
        candidate_ids += _extract_msgids(references)

        parent = None
        if candidate_ids:
            parent = request.env["mail.message"].sudo().search(
                [("message_id", "in", candidate_ids)],
                order="id desc",
                limit=1
            )

        # 2) Si encontramos parent, publicamos en el mismo documento
        if parent and parent.model and parent.res_id:
            request.env["mail.message"].sudo().create({
                "subject": subject,
                "body": body,
                "email_from": email_from,
                "message_id": msgid or False,
                "reply_to": False,
                "model": parent.model,
                "res_id": parent.res_id,
                "message_type": "comment",
                "subtype_id": request.env.ref("mail.mt_comment").id,
                "parent_id": parent.id,
            })
            return {"status": "ok", "linked": True, "model": parent.model, "res_id": parent.res_id}

        # 3) Fallback: si no hay parent, lo colgamos en un lugar “buzón”
        request.env["mail.message"].sudo().create({
            "subject": f"[UNLINKED] {subject}",
            "body": body,
            "email_from": email_from,
            "message_id": msgid or False,
            "model": "res.partner",
            "res_id": 1,
            "message_type": "comment",
            "subtype_id": request.env.ref("mail.mt_comment").id,
        })
        return {"status": "ok", "linked": False}