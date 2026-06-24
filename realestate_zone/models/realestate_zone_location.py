from odoo import api, fields, models


class RealEstateZoneLocation(models.Model):
    _name = "realestate.zone.location"
    _description = "Zone Knowledge Location"
    _inherit = ["realestate.property", "mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"

    occupant_info = fields.Char(
        string="Owner / Inhabitants",
        help="Free-text information about who owns or lives in the property "
             "(may be informal, e.g. 'elderly couple').",
    )
    sale_potential = fields.Selection(
        selection=[("low", "Low"), ("medium", "Medium"), ("high", "High")],
        string="Sale Potential",
        default="medium",
        tracking=True,
        help="Estimated likelihood that this property becomes a future sale "
             "opportunity.",
    )
    # --- Contact / follow-up ---
    contact_name = fields.Char(
        string="Contact Name",
        help="Name of the person to contact about this property in the future.",
    )
    contact_phone = fields.Char(
        string="Contact Phone",
        help="Phone number to reach the contact.",
    )
    contact_email = fields.Char(
        string="Contact Email",
        help="Email address of the contact.",
    )
    best_contact_time = fields.Char(
        string="Best Time to Contact",
        help="Preferred moment / time of day to contact this person.",
    )
    last_contact_date = fields.Date(
        string="Last Contact",
        help="Date of the last contact with this person.",
    )
    next_contact_date = fields.Date(
        string="Next Contact",
        help="Planned date for the next follow-up contact.",
    )
    rapport_notes = fields.Text(
        string="Rapport / Personal Notes",
        help="Personal details that help build a closer, trusting relationship "
             "(interests, family, important dates, etc.).",
    )
    # --- The two observation fields requested ---
    observation_1 = fields.Text(
        string="Observations 1",
        help="First free-text observations field.",
    )
    observation_2 = fields.Text(
        string="Observations 2",
        help="Second free-text observations field.",
    )
    # --- Lines (units / departments of a building or finca) ---
    unit_ids = fields.One2many(
        comodel_name="realestate.zone.unit",
        inverse_name="location_id",
        string="Units / Departments",
        help="Individual units (e.g. apartments in a building or plots in a "
             "'finca') that are also potential future sale opportunities.",
    )
    unit_count = fields.Integer(
        string="Units",
        compute="_compute_unit_count",
        help="Number of units registered for this location.",
    )

    @api.depends("unit_ids")
    def _compute_unit_count(self):
        for record in self:
            record.unit_count = len(record.unit_ids)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("name") or vals.get("name") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("realestate.zone.location")
                    or "New"
                )
        return super().create(vals_list)
