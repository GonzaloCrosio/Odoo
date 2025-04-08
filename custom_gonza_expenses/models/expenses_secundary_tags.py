from odoo import models, fields


class ExpensesSecundaryTags(models.Model):
    _description = "Expenses Tags"
    _name = "exp.tag.secundary.expenses"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "custom_name"

    custom_name = fields.Char(
        string="Expenses Secundary Tag",
        required=True,
    )
    description = fields.Text(
        string="Description",
    )
