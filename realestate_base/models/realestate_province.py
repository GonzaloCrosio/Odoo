from odoo import fields, models


class RealEstateProvince(models.Model):
    _name = "realestate.province"
    _description = "Argentine Province"
    _order = "name"

    name = fields.Char(
        string="Province",
        required=True,
        help="Name of the Argentine province (or autonomous city).",
    )
    code = fields.Char(
        string="Code",
        help="ISO 3166-2 code of the province, e.g. AR-B for Buenos Aires.",
    )
    country_id = fields.Many2one(
        comodel_name="res.country",
        string="Country",
        help="Country the province belongs to. Used to auto-fill the country "
             "on a property when the province is selected.",
    )
    active = fields.Boolean(
        string="Active",
        default=True,
        help="Uncheck to archive this province without deleting it.",
    )
