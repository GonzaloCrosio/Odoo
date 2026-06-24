from odoo import api, fields, models


class RealEstateSaleProperty(models.Model):
    _name = "realestate.sale.property"
    _description = "Property for Sale"
    _inherit = ["realestate.property", "mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"

    state = fields.Selection(
        selection=[
            ("portfolio", "In Portfolio"),
            ("sold", "Sold"),
            ("inactive", "Inactive"),
        ],
        string="Status",
        default="portfolio",
        required=True,
        tracking=True,
        help="Commercial situation of the property: In Portfolio (listed and "
             "offered for sale), Sold, or Inactive (could not be sold and is "
             "no longer offered).",
    )
    # --- Valuation (all Float, as requested) ---
    client_expected_value = fields.Float(
        string="Owner's Expected Value",
        tracking=True,
        help="Sale value expected by the owner / client.",
    )
    current_sale_value = fields.Float(
        string="Current Sale Value",
        tracking=True,
        help="Current asking sale value of the property.",
    )
    market_price = fields.Float(
        string="Market Price",
        help="Estimated market price based on comparable properties.",
    )
    safe_sale_value = fields.Float(
        string="Safe Sale Value",
        help="Conservative value at which a quick / safe sale is expected.",
    )
    # --- Dates / counterpart ---
    listing_date = fields.Date(
        string="Listing Date",
        default=fields.Date.context_today,
        help="Date the property entered the portfolio.",
    )
    sale_date = fields.Date(
        string="Sale Date",
        help="Date on which the property was sold.",
    )
    buyer_id = fields.Many2one(
        comodel_name="res.partner",
        string="Buyer",
        help="Contact who purchased the property.",
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("name") or vals.get("name") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("realestate.sale.property")
                    or "New"
                )
        return super().create(vals_list)

    def action_set_portfolio(self):
        self.write({
            "state": "portfolio",
        })

    def action_set_sold(self):
        self.write({
            "state": "sold",
            "sale_date": fields.Date.context_today(self),
        })

    def action_set_inactive(self):
        self.write({
            "state": "inactive",
        })
