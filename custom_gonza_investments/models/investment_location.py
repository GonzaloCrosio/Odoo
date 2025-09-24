from odoo import models, fields


class InvestmentLocation(models.Model):
    _description = "Investment Location"
    _name = "investment.location"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "custom_name"

    custom_name = fields.Char(
        string="Investment Location",
        required=True,
    )
    description = fields.Text(
        string="Description",
    )
