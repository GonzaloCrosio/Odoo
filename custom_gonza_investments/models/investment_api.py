# Este modelo sirve para actualizar el precio de las criptomonedas
# desde una API externa y actualizar los precios en los activos relacionados.

import logging
import requests
from odoo import models, fields, api

_logger = logging.getLogger(__name__)

class InvestmentCryptoPrice(models.Model):
    _name = 'investment.crypto.price'
    _description = 'Cryptocurrency Prices'
    _inherit = ["mail.thread", "mail.activity.mixin"]

    # Campos para almacenar los valores
    bitcoin_price = fields.Float(
        string="Price BTC (USD)"
    )
    xrp_price = fields.Float(
        string="Price XRP (USD)"
    )
    hbar_price = fields.Float(
        string="Price HBAR (USD)"
    )
    bitcoin_market_cap = fields.Float(
        string="Market capitalization BTC (USD)"
    )
    xrp_market_cap = fields.Float(
        string="Market capitalization XRP (USD)"
    )
    hbar_market_cap = fields.Float(
        string="Market capitalization HBAR (USD)"
    )
    bitcoin_ranking = fields.Integer(
        string="Ranking BTC"
    )
    xrp_ranking = fields.Integer(
        string="Ranking XRP"
    )
    hbar_ranking = fields.Integer(
        string="Ranking HBAR"
    )
    bitcoin_dominance = fields.Float(
        string="BTC Dominance %"
    )
    xrp_dominance = fields.Float(
        string="XRP Dominance %"
    )
    hbar_dominance = fields.Float(
        string="HBAR Dominance %"
    )

    # Metodo para obtener precios desde API CoinMarketCap
    @api.model
    def update_crypto_prices(self):
        # Endpoint y headers de la API
        url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
        headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': 'e195ad49-8340-4ae9-8897-5e06ebdaa143',
        }

        # Criptomonedas a consultar
        params = {
            'symbol': 'BTC,XRP,HBAR',
            'convert': 'USD'
        }

        try:
            # Realizamos la solicitud
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()  # Verifica si hubo errores HTTP
            data = response.json()

            # Obtenemos las respuestas de la API
            btc_price = data['data']['BTC']['quote']['USD']['price']
            xrp_price = data['data']['XRP']['quote']['USD']['price']
            hbar_price = data['data']['HBAR']['quote']['USD']['price']
            btc_capitalization = data['data']['BTC']['quote']['USD']['market_cap']
            xrp_capitalization = data['data']['XRP']['quote']['USD']['market_cap']
            hbar_capitalization = data['data']['HBAR']['quote']['USD']['market_cap']
            btc_ranking = data['data']['BTC']['cmc_rank']
            xrp_rank = data['data']['XRP']['cmc_rank']
            hbar_rank = data['data']['HBAR']['cmc_rank']
            btc_dominance = data['data']['BTC']['quote']['USD']['market_cap_dominance']
            xrp_dominance_cap = data['data']['XRP']['quote']['USD']['market_cap_dominance']
            hbar_dominance_cap = data['data']['HBAR']['quote']['USD']['market_cap_dominance']


            # Verifica si existe al menos un registro
            record = self.search([], limit=1)
            if record:
                # Actualizamos los campos en el registro encontrado
                record.sudo().write({
                    'bitcoin_price': btc_price,
                    'xrp_price': xrp_price,
                    'hbar_price': hbar_price,
                    'bitcoin_market_cap': btc_capitalization,
                    'xrp_market_cap': xrp_capitalization,
                    'hbar_market_cap': hbar_capitalization,
                    'bitcoin_ranking': btc_ranking,
                    'xrp_ranking': xrp_rank,
                    'hbar_ranking': hbar_rank,
                    'bitcoin_dominance': btc_dominance,
                    'xrp_dominance': xrp_dominance_cap,
                    'hbar_dominance': hbar_dominance_cap
                })
            else:
                # Crea un registro si no existe ninguno
                self.create({
                    'bitcoin_price': btc_price,
                    'xrp_price': xrp_price,
                    'hbar_price': hbar_price,
                    'bitcoin_market_cap': btc_capitalization,
                    'xrp_market_cap': xrp_capitalization,
                    'hbar_market_cap': hbar_capitalization,
                    'bitcoin_ranking': btc_ranking,
                    'xrp_ranking': xrp_rank,
                    'hbar_ranking': hbar_rank,
                    'bitcoin_dominance': btc_dominance,
                    'xrp_dominance': xrp_dominance_cap,
                    'hbar_dominance': hbar_dominance_cap
                })

        # Error si la solicitud falla
        except requests.exceptions.RequestException as e:
            _logger.error(f"Fail conexion with CoinMarketCap API: {e}")
        # Error si el dato se busca mal en las respuestas de la API
        except KeyError as e:
            _logger.error(f"API response structure error: {e}")

        # Actualiza los precios de los activos
        self.update_assets_prices()

    # Cron para actualización de precios automáticamente - Acciones planificadas
    @api.model
    def cron_update_prices(self):
        self.update_crypto_prices()

    def update_assets_prices(self):
        """
        Metodo que actualiza el campo `current_price` en los registros de `investment.assets`
        después de que cambien los precios de las criptomonedas.
        """
        # Recupera el registro actualizado de `investment.crypto.price`
        crypto_prices = self.search([], limit=1,
                                    order='id desc')  # Obtén el registro más reciente
        if not crypto_prices:
            return  # Si no hay registro, no hace nada

        # Busca todos los registros de `investment.assets` donde `asset_type` sea 'crypto'
        assets = self.env['investment.assets'].search(
            [('asset_type', '=', 'crypto')])
        for asset in assets:
            # Actualiza el precio basado en `custom_name`
            if asset.custom_name == 'Bitcoin':
                asset.sudo().write({'current_price': crypto_prices.bitcoin_price})
            elif asset.custom_name == 'XRP':
                asset.sudo().write({'current_price': crypto_prices.xrp_price})
            elif asset.custom_name == 'HBAR':
                asset.sudo().write({'current_price': crypto_prices.hbar_price})

        # Actualiza los precios en investment.total y investment.property si es necesario
        # total_assets = self.env['investment.total'].search(
        #     [('total_investment_asset_type', '=', 'crypto')])
        # for total_asset in total_assets:
        #     # Actualiza el precio basado en `custom_name`
        #     if total_asset.name == 'Bitcoin':
        #         total_asset.sudo().write({'current_price': crypto_prices.bitcoin_price})
        #     elif total_asset.name == 'XRP':
        #         total_asset.sudo().write({'current_price': crypto_prices.xrp_price})
        #     elif total_asset.name == 'HBAR':
        #         total_asset.sudo().write({'current_price': crypto_prices.hbar_price})
        #
        # properties = self.env['investment.property'].search(
        #     [('property_asset_type', '=', 'crypto')])
        # for property in properties:
        #     # Actualiza el precio basado en `display_name`
        #     if property.display_name == 'Bitcoin':
        #         property.sudo().write({'unit_current_price': crypto_prices.bitcoin_price})
        #     elif property.display_name == 'XRP':
        #         property.sudo().write({'unit_current_price': crypto_prices.xrp_price})
        #     elif property.display_name == 'HBAR':
        #         property.sudo().write({'unit_current_price': crypto_prices.hbar_price})


