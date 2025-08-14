from odoo import models, fields


class ExpensesType(models.Model):
    _description = "Related Operation"
    _name = "exp.expenses.type"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "custom_name"

    custom_name = fields.Char(
        string="Related Operation",
        required=True,
    )
    description = fields.Text(
        string="Description",
    )
