from odoo import models, fields


class ExpensesTags(models.Model):
    _description = "Expenses Tags"
    _name = "exp.tag.expenses"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "custom_name"

    custom_name = fields.Char(
        string="Expenses Tag",
        required=True,
        translate=True,
    )
    description = fields.Text(
        string="Description",
    )
    compatible_secundary_tags_ids = fields.Many2many(
        comodel_name="exp.tag.secundary.expenses",
        string="Compatible Secondary Tags",
        help="Select the secondary tags compatible with this principal tag.",
    )
