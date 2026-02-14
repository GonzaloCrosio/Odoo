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
        string="Current Price (USD)",
        readonly=True,
    )
    market_cap_usd = fields.Float(
        related="asset_id.market_cap_usd",
        string="Market Cap (USD)",
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
        string="Market Value (USD)",
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

    @api.depends("asset_id", "company_id")
    def _compute_position(self):
        Purchase = self.env["crypto.valuation.layer"]
        for holding in self:
            if not holding.asset_id or not holding.company_id:
                holding.qty_available = 0.0
                holding.value_usd = 0.0
                continue

            # Todas las compras de ese asset y compañía
            layers = Purchase.search(
                [
                    ("asset_id", "=", holding.asset_id.id),
                    ("company_id", "=", holding.company_id.id),
                ]
            )

            qty = sum(
                layers.mapped("qty_available")
            )  # ya lo calculas en el modelo FIFO
            holding.qty_available = qty
            holding.value_usd = qty * (holding.current_price_usd or 0.0)

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
