# Este modelo sirve para actualizar el precio de las criptomonedas
# desde una API externa y actualizar los precios en los activos relacionados.

import logging

import requests

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class InvestmentCryptoPrice(models.Model):
    _name = "investment.crypto.price"
    _description = "Cryptocurrency Prices"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    # Campos para almacenar los valores
    bitcoin_price = fields.Float(
        string="Price BTC (USD)",
    )
    xrp_price = fields.Float(
        string="Price XRP (USD)",
    )
    hbar_price = fields.Float(
        string="Price HBAR (USD)",
    )
    bitcoin_market_cap = fields.Float(
        string="Market capitalization BTC (USD)",
    )
    xrp_market_cap = fields.Float(
        string="Market capitalization XRP (USD)",
    )
    hbar_market_cap = fields.Float(
        string="Market capitalization HBAR (USD)",
    )
    bitcoin_ranking = fields.Integer(
        string="Ranking BTC",
    )
    xrp_ranking = fields.Integer(
        string="Ranking XRP",
    )
    hbar_ranking = fields.Integer(
        string="Ranking HBAR",
    )
    bitcoin_dominance = fields.Float(
        string="BTC Dominance %",
    )
    xrp_dominance = fields.Float(
        string="XRP Dominance %",
    )
    hbar_dominance = fields.Float(
        string="HBAR Dominance %",
    )
    fear_greed_value = fields.Integer(
        string="CMC Fear & Greed",
    )
    fear_greed_classification = fields.Char(
        string="F&G Classification",
    )

    # Metodo para obtener precios desde API CoinMarketCap
    @api.model
    def update_crypto_prices(self):
        # Leer API Key desde Parámetros del Sistema
        api_key = self.env["ir.config_parameter"].sudo().get_param("crypto.api_key")

        if not api_key:
            _logger.error(
                "API key not configured in System Parameters (crypto.api_key)"
            )
            return

        # Endpoint y headers de la API
        url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
        headers = {
            "Accepts": "application/json",
            "X-CMC_PRO_API_KEY": api_key,
        }

        # Criptomonedas a consultar
        params = {"symbol": "BTC,XRP,HBAR", "convert": "USD"}

        try:
            # Realizamos la solicitud
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()  # Verifica si hubo errores HTTP
            data = response.json()

            # Obtenemos las respuestas de la API
            btc_price = data["data"]["BTC"]["quote"]["USD"]["price"]
            xrp_price = data["data"]["XRP"]["quote"]["USD"]["price"]
            hbar_price = data["data"]["HBAR"]["quote"]["USD"]["price"]
            btc_capitalization = data["data"]["BTC"]["quote"]["USD"]["market_cap"]
            xrp_capitalization = data["data"]["XRP"]["quote"]["USD"]["market_cap"]
            hbar_capitalization = data["data"]["HBAR"]["quote"]["USD"]["market_cap"]
            btc_ranking = data["data"]["BTC"]["cmc_rank"]
            xrp_rank = data["data"]["XRP"]["cmc_rank"]
            hbar_rank = data["data"]["HBAR"]["cmc_rank"]
            btc_dominance = data["data"]["BTC"]["quote"]["USD"]["market_cap_dominance"]
            xrp_dominance_cap = data["data"]["XRP"]["quote"]["USD"][
                "market_cap_dominance"
            ]
            hbar_dominance_cap = data["data"]["HBAR"]["quote"]["USD"][
                "market_cap_dominance"
            ]

            # Verifica si existe al menos un registro
            record = self.search([], limit=1)
            if record:
                # Actualizamos los campos en el registro encontrado
                record.sudo().write(
                    {
                        "bitcoin_price": btc_price,
                        "xrp_price": xrp_price,
                        "hbar_price": hbar_price,
                        "bitcoin_market_cap": btc_capitalization,
                        "xrp_market_cap": xrp_capitalization,
                        "hbar_market_cap": hbar_capitalization,
                        "bitcoin_ranking": btc_ranking,
                        "xrp_ranking": xrp_rank,
                        "hbar_ranking": hbar_rank,
                        "bitcoin_dominance": btc_dominance,
                        "xrp_dominance": xrp_dominance_cap,
                        "hbar_dominance": hbar_dominance_cap,
                    }
                )
            else:
                # Crea un registro si no existe ninguno
                self.create(
                    {
                        "bitcoin_price": btc_price,
                        "xrp_price": xrp_price,
                        "hbar_price": hbar_price,
                        "bitcoin_market_cap": btc_capitalization,
                        "xrp_market_cap": xrp_capitalization,
                        "hbar_market_cap": hbar_capitalization,
                        "bitcoin_ranking": btc_ranking,
                        "xrp_ranking": xrp_rank,
                        "hbar_ranking": hbar_rank,
                        "bitcoin_dominance": btc_dominance,
                        "xrp_dominance": xrp_dominance_cap,
                        "hbar_dominance": hbar_dominance_cap,
                    }
                )

        # Error si la solicitud falla
        except requests.exceptions.RequestException as e:
            _logger.error(f"Fail conexion with CoinMarketCap API: {e}")
        # Error si el dato se busca mal en las respuestas de la API
        except KeyError as e:
            _logger.error(f"API response structure error: {e}")

        # Actualiza los precios de los activos
        self.update_assets_prices()

    # Cron para actualización de precios automáticamente - Acciones planificadas
    # También actualiza el índice de miedo y codicia
    @api.model
    def cron_update_prices(self):
        self.update_crypto_prices()
        self.update_fear_greed()

    def update_assets_prices(self):
        """
        Actualiza los campos de 'crypto.asset' con los valores obtenidos
        desde CoinMarketCap (BTC, XRP, HBAR).
        """
        # Tomamos el registro más reciente de precios
        crypto_prices = self.search([], limit=1, order="id desc")
        if not crypto_prices:
            return

        CryptoAsset = self.env["crypto.asset"]

        # Mapeamos cada symbol a los valores correspondientes en el modelo de precios
        mapping = {
            "BTC": {
                "price_usd": crypto_prices.bitcoin_price,
                "market_cap_usd": crypto_prices.bitcoin_market_cap,
                "cmc_rank": crypto_prices.bitcoin_ranking,
                "dominance_percentage": crypto_prices.bitcoin_dominance,
            },
            "XRP": {
                "price_usd": crypto_prices.xrp_price,
                "market_cap_usd": crypto_prices.xrp_market_cap,
                "cmc_rank": crypto_prices.xrp_ranking,
                "dominance_percentage": crypto_prices.xrp_dominance,
            },
            "HBAR": {
                "price_usd": crypto_prices.hbar_price,
                "market_cap_usd": crypto_prices.hbar_market_cap,
                "cmc_rank": crypto_prices.hbar_ranking,
                "dominance_percentage": crypto_prices.hbar_dominance,
            },
        }

        # Buscamos los assets que tengan esos symbols
        assets = CryptoAsset.search([("symbol", "in", list(mapping.keys()))])
        for asset in assets:
            vals = mapping.get(asset.symbol)
            if vals:
                asset.sudo().write(vals)

    # API para actualizar el índice de miedo y codicia
    def _fetch_cmc_fear_greed_latest(self, api_key):
        url = "https://pro-api.coinmarketcap.com/v3/fear-and-greed/latest"
        headers = {
            "Accepts": "application/json",
            "X-CMC_PRO_API_KEY": api_key,
        }

        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()  # Verifica que no existe errores de conexión
        payload = response.json()

        data = payload.get("data")
        if not data:
            return None

        item = data[0] if isinstance(data, list) else data

        return {
            "fear_greed_value": item.get("value"),
            "fear_greed_classification": item.get("value_classification"),
        }

    @api.model
    def update_fear_greed(self):
        # Parámetro del API en Parámetros del Sistema
        api_key = self.env["ir.config_parameter"].sudo().get_param("crypto.api_key")
        if not api_key:
            _logger.error(
                "API key not configured in System Parameters (crypto.api_key)"
            )
            return

        try:
            fng_vals = self._fetch_cmc_fear_greed_latest(api_key)
            if not fng_vals:
                return

            record = self.search([], limit=1)
            if record:
                record.sudo().write(fng_vals)
            else:
                self.create(fng_vals)

        except requests.exceptions.RequestException as e:
            _logger.error(f"Fail conexion Fear&Greed CoinMarketCap API: {e}")
        except KeyError as e:
            _logger.error(f"Fear&Greed API response structure error: {e}")
