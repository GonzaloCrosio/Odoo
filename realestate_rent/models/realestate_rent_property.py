from odoo import api, fields, models


class RealEstateRentProperty(models.Model):
    _name = "realestate.rent.property"
    _description = "Property for Rent"
    _inherit = ["realestate.property", "mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"

    state = fields.Selection(
        selection=[
            ("available", "Available"),
            ("rented", "Rented"),
            ("inactive", "Inactive"),
        ],
        string="Status",
        default="available",
        required=True,
        tracking=True,
        help="Commercial situation of the property: Available (listed and "
             "offered for rent), Rented, or Inactive (no longer offered).",
    )
    rent_period = fields.Selection(
        selection=[
            ("monthly", "Monthly"),
            ("quarterly", "Quarterly"),
            ("yearly", "Yearly"),
        ],
        string="Rent Period",
        default="monthly",
        help="Billing period the rent values refer to.",
    )
    # --- Valuation (all Float, as requested) ---
    client_expected_rent = fields.Float(
        string="Owner's Expected Rent",
        tracking=True,
        help="Rent value expected by the owner / client per period.",
    )
    current_rent_value = fields.Float(
        string="Current Rent Value",
        tracking=True,
        help="Current asking rent value of the property per period.",
    )
    market_rent = fields.Float(
        string="Market Rent",
        help="Estimated market rent based on comparable properties.",
    )
    safe_rent_value = fields.Float(
        string="Safe Rent Value",
        help="Conservative rent value at which a quick / safe rental is expected.",
    )
    deposit = fields.Float(
        string="Security Deposit",
        help="Security deposit required to rent the property.",
    )
    # --- Tenant / contract ---
    tenant_id = fields.Many2one(
        comodel_name="res.partner",
        string="Tenant",
        help="Current tenant of the property.",
    )
    available_date = fields.Date(
        string="Available Since",
        default=fields.Date.context_today,
        help="Date the property became available for rent.",
    )
    contract_start = fields.Date(
        string="Contract Start",
        help="Start date of the current rental contract.",
    )
    contract_end = fields.Date(
        string="Contract End",
        help="End date of the current rental contract.",
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("name") or vals.get("name") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("realestate.rent.property")
                    or "New"
                )
        return super().create(vals_list)

    def action_set_available(self):
        self.write({
            "state": "available",
        })

    def action_set_rented(self):
        self.write({
            "state": "rented",
            "contract_start": fields.Date.context_today(self),
        })

    def action_set_inactive(self):
        self.write({
            "state": "inactive",
        })
