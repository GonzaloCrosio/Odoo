from odoo import models, fields


class ExpensesPaymentMode(models.Model):
    _description = "Expenses Payment Mode"
    _name = "exp.expenses.payment.mode"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "custom_name"

    custom_name = fields.Char(
        string="Expenses Payment Mode",
        required=True,
    )
