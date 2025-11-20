# Este modelo sirve para almacenar las asignaciones de ventas de criptomonedas

from odoo import api, fields, models


class CryptoSaleAllocation(models.Model):
    _name = "crypto.sale.allocation"
    _description = "Crypto Sale Allocation (FIFO)"
    _order = "id asc"
    _rec_name = "asset_id"

    sale_line_id = fields.Many2one(
        "crypto.sale.line",
        required=True,
        string="Sale Line",
        ondelete="restrict",  # Borrar asignaciones al borrar línea de venta
    )
    # Línea de compra de la que se extrae esta asignación
    in_layer_id = fields.Many2one(
        "crypto.valuation.layer",
        required=True,
        ondelete="restrict",
        string="Purcharse Line",
    )
    date = fields.Datetime(
        required=True,
        string="Date",
    )
    qty_sold = fields.Float(
        required=True, digits="Product Unit of Measure", string="Qty Sold"
    )
    proceeds_unit_eur = fields.Monetary(
        currency_field="currency_id",
        required=True,
        string="Unit Price (EUR)",
    )
    unit_cost_eur = fields.Monetary(
        currency_field="currency_id",
        required=True,
        string="Unit cost (EUR)",
    )
    fee_unit_eur = fields.Monetary(
        currency_field="currency_id",
        default=0.0,
        string="Unit Fee (EUR)",
    )
    currency_id = fields.Many2one(
        related="sale_line_id.currency_id",
        store=True,
        string="Currency",
    )
    company_id = fields.Many2one(
        related="sale_line_id.company_id",
        store=True,
        string="Company",
    )
    asset_id = fields.Many2one(
        "crypto.asset",
        related="sale_line_id.asset_id",
        store=True,
        index=True,
        string="Crypto Asset",
    )
    proceeds_eur = fields.Monetary(
        compute="_compute_amounts",
        currency_field="currency_id",
        store=True,
        string="Total (EUR)",
    )
    cost_eur = fields.Monetary(
        compute="_compute_amounts",
        currency_field="currency_id",
        store=True,
        string="Total cost (EUR)",
    )
    fee_eur = fields.Monetary(
        compute="_compute_amounts",
        currency_field="currency_id",
        store=True,
        string="Total fee (EUR)",
    )
    profit_eur = fields.Monetary(
        compute="_compute_amounts",
        currency_field="currency_id",
        store=True,
        string="Net Profit (EUR)",
    )
    tax_eur = fields.Monetary(
        compute="_compute_amounts",
        currency_field="currency_id",
        store=True,
        string="Spain Tax (EUR)",
    )

    @api.depends("qty_sold", "proceeds_unit_eur", "unit_cost_eur", "fee_unit_eur")
    def _compute_amounts(self):
        for crypto in self:
            crypto.proceeds_eur = crypto.qty_sold * crypto.proceeds_unit_eur
            crypto.cost_eur = crypto.qty_sold * crypto.unit_cost_eur
            crypto.fee_eur = crypto.qty_sold * (crypto.fee_unit_eur or 0.0)
            crypto.profit_eur = crypto.proceeds_eur - crypto.cost_eur - crypto.fee_eur
            crypto.tax_eur = self._compute_tax_fifo(crypto.profit_eur)

    # Calcula el impuesto según normativa española (FIFO)
    @api.model
    def _compute_tax_fifo(self, profit_eur):
        # Cálculo de IRPF ahorro (España) por tramos para UNA ganancia
        profit = max(profit_eur or 0.0, 0.0)

        if profit <= 6000:
            return profit * 0.19
        elif profit <= 50000:
            return 6000 * 0.19 + (profit - 6000) * 0.21
        elif profit <= 200000:
            return 6000 * 0.19 + (50000 - 6000) * 0.21 + (profit - 50000) * 0.23
        else:
            return (
                6000 * 0.19
                + (50000 - 6000) * 0.21
                + (200000 - 50000) * 0.23
                + (profit - 200000) * 0.26
            )

    def unlink(self):
        # Revertir qty_sold al borrar asignaciones
        for crypto in self:
            layer = crypto.in_layer_id.sudo()
            # pequeño margen por flotantes
            layer.qty_sold = max(0.0, layer.qty_sold - crypto.qty_sold)
        return super().unlink()
