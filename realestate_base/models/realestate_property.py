from odoo import api, fields, models


class RealEstateProperty(models.AbstractModel):
    """Abstract base shared by Sale, Rent and Zone properties.
    It centralises the fields common to every kind of property record so
    they are defined only once (owner, address, physical characteristics,
    currency).
    """
    _name = "realestate.property"
    _description = "Real Estate Property (Abstract Base)"

    def _default_country_id(self):
        country = self.env.ref("base.ar", raise_if_not_found=False)
        return country.id if country else False

    name = fields.Char(
        string="Reference",
        required=True,
        copy=False,
        default="New",
        help="Internal reference of the property. Generated automatically "
             "from a sequence when left empty.",
    )
    active = fields.Boolean(
        string="Active",
        default=True,
        help="If unchecked, the record is archived: hidden from default views "
             "without being deleted.",
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Owner",
        help="Contact who owns the property (seller / landlord).",
    )
    property_type_id = fields.Many2one(
        comodel_name="realestate.property.type",
        string="Property Type",
        help="Type of property. The available values are managed by the user "
             "under Real Estate > Configuration > Property Types.",
    )
    # --- Address ---
    street = fields.Char(
        string="Street",
        help="Street name and number of the property.",
    )
    zip = fields.Char(
        string="Postal Code",
        help="ZIP / postal code of the property.",
    )
    neighborhood = fields.Char(
        string="Neighborhood",
        help="Neighborhood (barrio) where the property is located.",
    )
    state_id = fields.Many2one(
        comodel_name="realestate.province",
        string="Province",
        help="Argentine province where the property is located.",
    )
    country_id = fields.Many2one(
        comodel_name="res.country",
        string="Country",
        default=_default_country_id,
        help="Country where the property is located. Defaults to Argentina.",
    )
    # --- Physical characteristics ---
    total_area = fields.Float(
        string="Total Area (m2)",
        help="Total surface of the property in square meters.",
    )
    covered_area = fields.Float(
        string="Covered Area (m2)",
        help="Covered / built surface of the property in square meters.",
    )
    rooms = fields.Integer(
        string="Rooms",
        help="Total number of rooms.",
    )
    bedrooms = fields.Integer(
        string="Bedrooms",
        help="Number of bedrooms.",
    )
    bathrooms = fields.Integer(
        string="Bathrooms",
        help="Number of bathrooms.",
    )
    currency = fields.Selection(
        selection=[("usd", "USD"), ("ars", "ARS")],
        string="Currency",
        default="usd",
        help="Currency in which the property values are expressed. In Argentina "
             "sale prices are usually quoted in USD.",
    )
    description = fields.Text(
        string="Description",
        help="Free description / general notes about the property.",
    )

    @api.onchange("state_id")
    def _onchange_state_id(self):
        for record in self:
            if record.state_id and record.state_id.country_id:
                record.country_id = record.state_id.country_id
