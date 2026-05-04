# -*- coding: utf-8 -*-
"""
Extiende mail.thread para que los correos salientes de Odoo incluyan
los headers RFC 2822:
  - In-Reply-To: <message_id del mensaje anterior en el hilo>
  - References:  <todos los message_ids del hilo, del más antiguo al más reciente>

Esto hace que Gmail, Outlook y cualquier cliente de correo agrupe
los mensajes en el mismo hilo/conversación.
"""

import logging
from odoo import models

_logger = logging.getLogger(__name__)


class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    def _notify_by_email_get_headers(self, headers=None, **kwargs):
        """
        V19: el metodo recibe headers como keyword argument.
        Añadimos In-Reply-To y References para mantener el hilo
        en Gmail, Outlook y cualquier cliente de correo.
        """
        headers = super()._notify_by_email_get_headers(headers=headers, **kwargs) or {}

        # Necesitamos el mensaje actual — viene en kwargs en V19
        message = kwargs.get("message")
        if not message:
            return headers

        try:
            headers = self._add_thread_headers(headers, message)
        except Exception as e:
            _logger.warning(
                "[mail_thread_headers] Error añadiendo thread headers: %s", e, exc_info=True
            )

        return headers

    def _add_thread_headers(self, headers, message):
        """
        Busca los mensajes previos del hilo y construye
        In-Reply-To y References.
        """
        if not message.model or not message.res_id:
            return headers

        # Todos los mensajes del hilo anteriores al actual, ordenados por id
        thread_messages = self.env["mail.message"].sudo().search(
            [
                ("model", "=", message.model),
                ("res_id", "=", message.res_id),
                ("message_id", "!=", False),
                ("id", "!=", message.id),
                ("message_type", "in", ["email", "comment"]),
            ],
            order="id asc",
        )

        if not thread_messages:
            return headers

        # In-Reply-To → message_id del mensaje inmediatamente anterior
        previous = thread_messages.filtered(lambda m: m.id < message.id)
        if previous:
            parent_msgid = previous[-1].message_id
            headers["In-Reply-To"] = parent_msgid
            _logger.debug(
                "[mail_thread_headers] In-Reply-To=%s (msg id=%s)",
                parent_msgid, message.id,
            )

        # References → todos los message_ids del hilo en orden cronológico
        all_msgids = [m.message_id for m in thread_messages if m.message_id]
        if all_msgids:
            headers["References"] = " ".join(all_msgids)
            _logger.debug(
                "[mail_thread_headers] References con %d msgs (msg id=%s)",
                len(all_msgids), message.id,
            )

        return headers
