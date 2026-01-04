from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class DashboardControl(models.Model):
    _name = "dashboard.control"
    _description = "Dashboard Model"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name = "name"

    name = fields.Char(
        string="Name",
        required=True,
    )
