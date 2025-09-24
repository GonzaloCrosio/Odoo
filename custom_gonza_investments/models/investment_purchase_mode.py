from odoo import models, fields


class ExpensesPurchaseMode(models.Model):
    _description = "Investment Purchase Mode"
    _name = "investment.purchase.mode"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "custom_name"

    custom_name = fields.Char(
        string="Purchase Mode",
        required=True,
    )
    description = fields.Text(
        string="Description",
    )
