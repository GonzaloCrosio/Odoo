from odoo import fields, models


class RealEstateZoneUnit(models.Model):
    _name = "realestate.zone.unit"
    _description = "Zone Knowledge Unit / Department"
    _order = "location_id, sequence, id"

    location_id = fields.Many2one(
        comodel_name="realestate.zone.location",
        string="Location",
        required=True,
        ondelete="cascade",
        help="Parent location this unit belongs to.",
    )
    sequence = fields.Integer(
        string="Sequence",
        default=10,
        help="Order of the unit within the location.",
    )
    name = fields.Char(
        string="Unit / Department",
        required=True,
        help="Identifier of the unit (e.g. '3B', 'Depto 2', 'Lote 5').",
    )
    floor = fields.Char(
        string="Floor",
        help="Floor where the unit is located.",
    )
    property_type_id = fields.Many2one(
        comodel_name="realestate.property.type",
        string="Type",
        help="Type of this unit.",
    )
    occupant_info = fields.Char(
        string="Owner / Inhabitants",
        help="Who owns or lives in this unit.",
    )
    rooms = fields.Integer(
        string="Rooms",
        help="Number of rooms in the unit.",
    )
    bathrooms = fields.Integer(
        string="Bathrooms",
        help="Number of bathrooms in the unit.",
    )
    area = fields.Float(
        string="Area (m2)",
        help="Surface of the unit in square meters.",
    )
    sale_potential = fields.Selection(
        selection=[("low", "Low"), ("medium", "Medium"), ("high", "High")],
        string="Sale Potential",
        default="medium",
        help="Likelihood this unit becomes a future sale opportunity.",
    )
    observation = fields.Text(
        string="Observations",
        help="Free-text notes about this unit.",
    )
