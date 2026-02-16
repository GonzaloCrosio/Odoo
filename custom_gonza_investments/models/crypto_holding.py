from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class CryptoHolding(models.Model):
    _name = "crypto.holding"
    _description = "Crypto Holding (Position by Asset)"
    _rec_name = "asset_id"
    _order = "asset_id"
    _check_company_auto = True
    _inherit = ["mail.thread", "mail.activity.mixin"]

    asset_id = fields.Many2one(
        "crypto.asset",
        required=True,
        index=True,
        string="Asset",
    )
    company_id = fields.Many2one(
        "res.company",
        required=True,
        default=lambda self: self.env.company,
        index=True,
        string="Company",
    )
    currency_id = fields.Many2one(
        "res.currency",
        related="asset_id.currency_id",
        store=True,
        readonly=True,
        string="Currency",
    )
    # CANTIDAD TOTAL DISPONIBLE (suma de todas las capas de compra no vendidas)
    qty_available = fields.Float(
        compute="_compute_position",
        digits=(16, 8),
        string="Quantity Available",
        readonly=True,
    )
    # DATOS RELACIONADOS DEL ASSET (API)
    current_price_usd = fields.Float(
        related="asset_id.price_usd",
        string="Current Price (EUR)",
        readonly=True,
    )
    market_cap_usd = fields.Float(
        related="asset_id.market_cap_usd",
        string="Market Cap (EUR)",
        readonly=True,
    )
    cmc_rank = fields.Integer(
        related="asset_id.cmc_rank",
        string="CMC Rank",
        readonly=True,
    )
    dominance_percentage = fields.Float(
        related="asset_id.dominance_percentage",
        string="Dominance (%)",
        readonly=True,
    )
    # VALORIZACIÓN = precio actual * cantidad disponible
    value_usd = fields.Monetary(
        compute="_compute_position",
        currency_field="currency_id",
        string="Market Value (EUR)",
        readonly=True,
    )
    # Precio medio de Compra (Tenencia Activa, libre de ventas)
    avg_buy_price_eur = fields.Monetary(
        compute="_compute_position",
        currency_field="currency_id",
        string="Avg Buy Price",
        readonly=True,
    )
    # Costo Total de la Tenencia Activa (libre de ventas)
    cost_basis_eur = fields.Monetary(
        compute="_compute_position",
        currency_field="currency_id",
        string="Cost Basis",
        readonly=True,
        help="Total cost of the remaining position (only unsold quantities).",
    )
    # Resultado sin realizar en cantidad
    unrealized_pl_eur = fields.Monetary(
        compute="_compute_position",
        currency_field="currency_id",
        string="Unrealized P/L",
        readonly=True,
    )
    # Resultado sin realizar en porcentaje
    unrealized_return_pct = fields.Float(
        compute="_compute_position",
        digits=(16, 4),
        string="Unrealized Return (%)",
        readonly=True,
    )

    @api.constrains("asset_id", "company_id")
    def _check_unique_asset_company(self):
        for crypto in self:
            duplicate_count = self.search_count([
                ("asset_id", "=", crypto.asset_id.id),
                ("company_id", "=", crypto.company_id.id),
                ("id", "!=", crypto.id),
            ])
            if duplicate_count:
                raise ValidationError(_(
                    "Each asset can only have one holding per company.\n"
                    "Asset: %s\nCompany: %s"
                ) % (crypto.asset_id.display_name, crypto.company_id.display_name))

    # Para calcular precios promedios, rentabilidades y cantidades
    @api.depends("asset_id", "company_id", "current_price_usd")
    def _compute_position(self):

        # Inicializamos valores para reasignarles el valor
        for h in self:
            h.qty_available = 0.0
            h.value_usd = 0.0
            h.cost_basis_eur = 0.0
            h.avg_buy_price_eur = 0.0
            h.unrealized_pl_eur = 0.0
            h.unrealized_return_pct = 0.0

        holdings = self.filtered(lambda h: h.asset_id and h.company_id)
        if not holdings:
            return

        # Preparamos las listas de IDs para la query
        asset_ids = tuple(set(holdings.mapped("asset_id").ids))
        company_ids = tuple(set(holdings.mapped("company_id").ids))

        # 1 sola query: qty_available total + remaining_cost total por (asset, company)
        # remaining_cost = (total_cost_eur + fee_eur) * (qty_available / qty_purchase)
        # qty_available está store=True en layer por eso uso SQL y evitos FOR anidados.
        self.env.cr.execute(
            """
            SELECT asset_id,
                   company_id,
                   COALESCE(SUM(qty_available), 0.0) AS qty_total,
                   COALESCE(SUM(
                                    CASE
                                        WHEN qty_purchase IS NULL OR qty_purchase = 0 OR qty_available <= 0
                                            THEN 0.0
                                        ELSE ((COALESCE(total_cost_eur, 0.0) + COALESCE(fee_eur, 0.0))
                                            * (qty_available / qty_purchase))
                                        END
                            ), 0.0)                  AS remaining_cost
            FROM crypto_valuation_layer
            WHERE asset_id IN %s
              AND company_id IN %s
            GROUP BY asset_id, company_id
            """,
            (asset_ids, company_ids),
        )

        # Pasar el resultado SQL a Lista
        aggregated = {
            (a, c): (qty, cost)
            for (a, c, qty, cost) in self.env.cr.fetchall()
        }

        # Asignar los valores según la lista obtenida
        for h in holdings:
            qty, cost = aggregated.get((h.asset_id.id, h.company_id.id), (0.0, 0.0))

            # Cantidad disponible
            h.qty_available = qty
            # Costo total
            h.cost_basis_eur = cost
            # Precio medio de compra
            h.avg_buy_price_eur = (cost / qty) if qty else 0.0

            # Tratamos el precio como EUR directamente y asignamos precio
            price = h.current_price_usd or 0.0
            h.value_usd = qty * price

            # P/L no realizado
            h.unrealized_pl_eur = h.value_usd - cost

            # Rentabilidad %
            h.unrealized_return_pct = (
                (h.unrealized_pl_eur / cost)
                if cost else 0.0
            )

    # Botón para abrir vista de compras filtrada por activo y compañía
    def action_open_valuation_layers(self):
        """Abrir las compras (valuation layers) de este asset."""
        self.ensure_one()
        action = self.env.ref(
            "custom_gonza_investments.action_crypto_valuation_layer"
        ).read()[0]
        action["domain"] = [
            ("asset_id", "=", self.asset_id.id),
            ("company_id", "=", self.company_id.id),
        ]
        return action