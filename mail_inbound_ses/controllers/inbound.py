from odoo import http
from odoo.http import request

class MailInboundController(http.Controller):

    @http.route("/mail/inbound", type="json", auth="public", methods=["POST"], csrf=False)
    def mail_inbound(self, **payload):
        subject = payload.get("subject") or "(sin asunto)"
        body = payload.get("body") or ""
        email_from = payload.get("from") or ""

        # Para probar: lo colgamos en el chatter del contacto Admin (partner id=1)
        request.env["mail.message"].sudo().create({
            "subject": subject,
            "body": body,
            "email_from": email_from,
            "model": "res.partner",
            "res_id": 1,
            "message_type": "comment",
        })

        return {"status": "ok"}