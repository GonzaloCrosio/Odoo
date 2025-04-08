from odoo import models, fields, api


class InvestmentAsstes(models.Model):
    _description = "Investment Assets"
    _name = "inv.investment.assets"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "custom_name"

    custom_name = fields.Char(
        string="Asset",
        required=True,
    )
    description = fields.Text(
        string="Description",
    )
    asset_type = fields.Selection(
        string="Asset Type",
        selection=[
            ('crypto', 'Crypto'),
            ('actions', 'Actions'),
            ('bonds', 'Bonds'),
            ('funds', 'Funds'),
            ('real_estate', 'Real Estate'),
            ('commodities', 'Commodities'),
            ('money_foreing_fiat', 'Foreign Fiat Money'),
            ('etf', 'ETF'),
            ('tourist_house', 'Tourist House'),
            ('traditional_business', 'Traditional Business'),
            ('others', 'Others'),
        ],
        required=True,
        default='crypto',
    )
    current_price = fields.Float(
        string="Current Price",
    )

