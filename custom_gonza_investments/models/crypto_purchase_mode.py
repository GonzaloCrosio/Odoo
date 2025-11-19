from odoo import models, fields


class CryptoPurchaseMode(models.Model):
    _description = "Crypto Purchase Mode"
    _name = "crypto.purchase.mode"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "custom_name"

    custom_name = fields.Char(
        string="Purchase Mode",
        required=True,
    )
    description = fields.Text(
        string="Description",
    )
