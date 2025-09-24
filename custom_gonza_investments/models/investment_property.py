from odoo import models, fields, api


class InvestmentProperty(models.Model):
    _description = "Investment Property"
    _name = "investment.property"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "custom_name"

    custom_name = fields.Many2one(
        string="Investment Property Name",
        comodel_name="investment.assets",
        required=True,
    )
    property_asset_type = fields.Selection(
        string="Property Asset Type",
        related="custom_name.asset_type",
    )
    description = fields.Text(
        string="Description",
    )
    quantity = fields.Float(
        string="Quantity",
        compute="_compute_quantity",
        digits=(16, 8)
    )
    unit_current_price = fields.Float(
        string="Unit Current Price",
    )
    current_amount = fields.Float(
        string="Current Amount",
        compute = "_compute_current_amount",
    )
    investment_id = fields.Many2one(
        comodel_name="investment.total",
        string="Related Investment",
        # domain="[('name', '=', custom_name.name)]",
    )
    property_type = fields.Selection(
        string="Property Type",
        selection=[
            ('Asset', 'Asset'),
            ('Liability', 'Liability'),
        ]
    )

    # Para que se actualice la cantidad de la propiedad en función de la cantidad de la inversión
    # Solo para inversiones variables
    @api.depends('investment_id.total_quantity_in_crypto')
    def _compute_quantity(self):
        """
        Calcula automáticamente la cantidad si el campo
        total_quantity_in_crypto cambia en investment.total.
        """
        for record in self:
            if record.investment_id:
                asset_type = record.investment_id.total_investment_asset_type
                if asset_type in ['crypto', 'actions', 'bonds', 'funds', 'etf']:
                    record.quantity = record.investment_id.total_quantity_in_crypto
                else:
                    record.quantity = 1
            else:
                record.quantity = 0

    @api.onchange('investment_id')
    def _onchange_investment_id(self):
        """
        Actualiza la cantidad según la inversión seleccionada en el formulario.
        """
        for record in self:
            if record.investment_id:
                asset_type = record.investment_id.total_investment_asset_type
                if asset_type in ['crypto', 'actions', 'bonds', 'funds', 'etf']:
                    record.quantity = record.investment_id.total_quantity_in_crypto
                else:
                    record.quantity = 1

    @api.depends('quantity', 'unit_current_price')
    def _compute_current_amount(self):
        for record in self:
            record.current_amount = record.quantity * record.unit_current_price
