from odoo import models, fields, api


class InvestmentTransaction(models.Model):
    _name = 'inv.investment.transaction'
    _description = 'Investment Transaction'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "investment_name"

    investment_name = fields.Many2one(
        comodel_name="inv.investment.assets",
        string="Investment Name",
        required=True
    )
    date = fields.Date(string="Transaction Date", required=True)
    description = fields.Text(string="Description")
    investment_asset_type = fields.Selection(
        string="Asset Type",
        related="investment_name.asset_type",
        required=True
    )
    status = fields.Selection(
        selection=[
            ('in_portfolio', 'In Portfolio'),
            ('sold', 'Sold')],
        string="Status"
    )
    strategy = fields.Selection(
        selection=[('trading', 'Trading'), ('holding', 'Holding')],
        string="Strategy",
        default='holding'
    )
    # Relación con las líneas
    line_ids = fields.One2many(
        comodel_name='inv.investment.transaction.line',
        inverse_name='transaction_id',
        string="Transaction Lines"
    )
    # Ubicación del activo
    investment_location_id = fields.Many2one(
        comodel_name="inv.investment.location",
        string="Investment location"
    )
    # Modo de compra
    investment_purchase_mode_id = fields.Many2one(
        comodel_name="inv.investment.purchase.mode",
        string="Buy Mode"
    )

    # @api.depends('line_ids.quantity_in_crypto', 'line_ids.quantity_in_fiat', 'line_ids.type')
    # def _compute_totals(self):
    #     for record in self:
    #         purchase_total = 0.0
    #         profit_total = 0.0
    #         for line in record.line_ids:
    #             if line.type == 'purchase':
    #                 purchase_total += line.quantity_in_crypto
    #             elif line.type == 'sale':
    #                 profit_total += line.profit
    #         record.quantity_in_fiat = purchase_total
    #         record.total_profit = profit_total
