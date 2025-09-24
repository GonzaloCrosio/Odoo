# Este modelo sirve para mapear las líneas de venta a las líneas de compra correspondientes
# en una estrategia FIFO (First In, First Out) para transacciones de criptomonedas
from odoo import api, fields, models


class InvestmentTransactionSaleLine(models.Model):
    _name = "investment.transaction.sale.line"
    _description = "Sale Line for Crypto FIFO matching"

    sale_transaction_id = fields.Many2one(
        comodel_name="investments.transactions",
        string="Sale Transaction",
        required=True,
        ondelete="cascade",
    )
    buy_transaction_id = fields.Many2one(
        comodel_name="investments.transactions",
        string="Related Buy Transaction",
        required=True,
    )
    quantity_used = fields.Float(
        string="Quantity Used from Buy", digits=(16, 8), required=True
    )
    buy_price_unit = fields.Float(
        string="Buy Price Unit", compute="_compute_buy_price_unit", store=True
    )

    @api.depends("buy_transaction_id")
    def _compute_buy_price_unit(self):
        for record in self:
            record.buy_price_unit = record.buy_transaction_id.transaction_price
