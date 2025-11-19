# Este modelo sirve para definir los activos de criptomonedas

from odoo import fields, models


class CryptoAsset(models.Model):
    _name = "crypto.asset"
    _description = "Crypto Asset"
    _rec_name = "symbol"
    _order = "symbol"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(
        required=True,
        string="Name",
    )
    symbol = fields.Char(
        required=True,
        index=True,
        string="Symbol",
    )
    company_id = fields.Many2one(
        "res.company",
        required=True,
        default=lambda self: self.env.company,
        string="Company",
    )
    currency_id = fields.Many2one(
        "res.currency",
        required=True,
        default=lambda self: self.env.ref(
            "base.EUR",
        ),
        string="Currency",
    )
    precision = fields.Integer(
        default=8,
        string="Precision",
    )
    price_usd = fields.Float(
        string="Price (USD)",
    )
    market_cap_usd = fields.Float(
        string="Market Cap (USD)",
    )
    cmc_rank = fields.Integer(
        string="CMC Rank",
    )
    dominance_percentage = fields.Float(
        string="Dominance (%)",
    )
