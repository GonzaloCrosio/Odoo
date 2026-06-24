from odoo import fields, models


class RealEstatePropertyType(models.Model):
    _name = "realestate.property.type"
    _description = "Real Estate Property Type"
    _order = "sequence, name"

    name = fields.Char(
        string="Name",
        required=True,
        translate=True,
        help="Name of the property type (dwelling, commercial premises, "
             "garage, etc.). Fully editable by the user.",
    )
    sequence = fields.Integer(
        string="Sequence",
        default=10,
        help="Defines the order in which property types are displayed.",
    )
    code = fields.Char(
        string="Code",
        help="Optional short code for the property type.",
    )
    active = fields.Boolean(
        string="Active",
        default=True,
        help="Uncheck to archive this property type without deleting it.",
    )
    description = fields.Text(
        string="Description",
        help="Optional description / notes about this property type.",
    )
