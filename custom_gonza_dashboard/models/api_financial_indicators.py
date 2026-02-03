# -*- coding: utf-8 -*-
import logging
import requests

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class FinancialIndicators(models.Model):
    _name = "financial.indicators"
    _description = "Financial Indicators"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(
        string="Name",
    )
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        required=True,
        default=lambda self: self.env.company.currency_id,
    )
    # Auditoría
    last_sync = fields.Datetime(
        string="Last Total Update",
        readonly=True,
        tracking=True,
    )
    last_sync_message = fields.Char(
        string="Result last sync",
        readonly=True,
    )
    # Config (Series IDs FRED) Campos (valores)
    # Liquidez / Fed
    tga_value = fields.Float(
        string="Treasury General Account (TGA)",
        help="The Treasury and Federal Reserve accounts."
             "The lower the account, the more money is in circulation.",
        tracking=True,
    )
    tga_date = fields.Date(
        string="TGA date",
        help="Last Update Date",
    )
    fred_series_tga = fields.Char(
        string="FRED series_id TGA",
        default="WTREGEN",
    )
    tga_link = fields.Char(
        string="Link FRED TGA",
        default="https://fred.stlouisfed.org/series/WTREGEN",
    )
    reserves_value = fields.Float(
        string="Bank Reserves",
        help="This is what banks use to invest—basically,"
             " our deposits. They depend to some extent on the TGA (Total Annual Growth Rate);"
             " if the US doesn't spend, no funds are deposited into the accounts of companies, individuals, etc.",
        tracking=True,
    )
    reserves_date = fields.Date(
        string="Update Date Bank Reserves",
        help="Last Update Date",
    )
    fred_series_reserves = fields.Char(
        string="FRED series_id Bank Reserves",
        default="WRESBAL",
    )
    reserves_link = fields.Char(
        string="Link FRED Reserves",
        default="https://fred.stlouisfed.org/series/WRESBAL",
    )
    srf_value = fields.Float(
        string="Standart Record Facility (SRF)",
        help="It is the instrument by which the Federal Reserve lends to banks that have access"
             " to it to prevent them from going bankrupt.",
        tracking=True,
    )
    srf_date = fields.Date(
        string="Update Date SRF",
        help="Last Update Date",
    )
    fred_series_srf = fields.Char(
        string="FRED series_id SRF",
        default="SRFTSYD",
    )
    srf_link = fields.Char(
        string="Link FRED SRF",
        default="https://fred.stlouisfed.org/series/SRFTSYD",
    )
    on_rrp_value = fields.Float(
        string="ON RRP",
        help="Excess Liquidity",
        tracking=True,
    )
    on_rrp_date = fields.Date(
        string="Update Date ON RRP",
        help="Last Update Date",
    )
    fred_series_on_rrp = fields.Char(
        string="FRED series_id ON RRP",
        default="RRPONTSYD",
    )
    on_rrp_link = fields.Char(
        string="Link FRED ON RRP",
        default="https://fred.stlouisfed.org/series/RRPONTSYD",
    )
    sofr_value = fields.Float(
        string="Secured Overnight Financing Rate (SOFR)",
        help="The interest rate at which banks lend money to each other",
        tracking=True,
    )
    sofr_date = fields.Date(
        string="Update Date SOFR",
        help="Last Update Date",
    )
    fred_series_sofr = fields.Char(
        string="FRED series_id SOFR",
        default="SOFR",
    )
    sofr_link = fields.Char(
        string="Link FRED SOFR",
        default="https://fred.stlouisfed.org/series/SOFR",
    )
    bonds_usa_value = fields.Float(
        string="Bonds USA Bank Reserva",
        help="If it goes up it provides more liquidity,"
             " and if it goes down it provides less liquidity.",
        tracking=True,
    )
    bonds_date = fields.Date(
        string="Update Date BONDS",
        help="Last Update Date",
    )
    fred_series_bonds = fields.Char(
        string="FRED series_id BONDS",
        default="treast",
    )
    bonds_link = fields.Char(
        string="Link FRED BONDS",
        default="https://fred.stlouisfed.org/series/treast",
    )
    inverse_repo_value = fields.Float(
        string="Inverse Repo USA",
        help="Overnight Repurchase Agreements: Treasury Securities Purchased"
             " by the Federal Reserve in the Temporary Open Market Operations,",
        tracking=True,
    )
    inverse_repo_date = fields.Date(
        string="Update Date Inverse Repo",
        help="Last Update Date",
    )
    fred_series_inverse_repo = fields.Char(
        string="FRED series_id Inverse Repo",
        default="RPONTSYD",
    )
    inverse_repo_link = fields.Char(
        string="Link FRED Inverse Repo",
        default="https://fred.stlouisfed.org/series/RPONTSYD",
    )
    # Mercados / índices
    usd_index_value = fields.Float(
        string="USD Index (DXY)",
        help="The USD's relationship to other currencies. "
             "The lower the value, the better for risk assets; if it rises, it's worse.",
        tracking=True,
    )
    usd_index_date = fields.Date(
        string="Update Date USD Index",
        help="Last Update Date",
    )
    fred_series_usd_index = fields.Char(
        string="FRED series_id USD Index (DXY/proxy)",
        default="DTWEXBGS",
    )
    usd_index_link = fields.Char(
        string="Link FRED USD Index",
        default="https://fred.stlouisfed.org/series/DTWEXBGS",
    )
    vix_value = fields.Float(
        string="Volatility Index (VIX)",
        tracking=True,
    )
    vix_date = fields.Date(
        string="Update Date VIX",
        help="Last Update Date",
    )
    fred_series_vix = fields.Char(
        string="FRED series_id VIX",
        default="VIXCLS",
    )
    vix_link = fields.Char(
        string="Link FRED VIX",
        default="https://fred.stlouisfed.org/series/VIXCLS",
    )
    move_value = fields.Float(
        string="Merrill Lynch Option Volatility Estimate (MOVE)",
        help="USA Bond Volatility - Manual Changes",
        tracking=True,
    )
    move_date = fields.Date(
        string="Update Date MOVE",
        help="Last Update Date",
    )
    fred_series_move = fields.Char(
        string="FRED series_id MOVE",
        default="",
    )
    move_link = fields.Char(
        string="Link FRED MOVE",
        default="https://es.tradingview.com/symbols/TVC-MOVE/?timeframe=1M",
    )
    # Macro
    inflation_cpi_value = fields.Float(
        string="USA Inflation",
        tracking=True,
    )
    inflation_cpi_date = fields.Date(
        string="Update Date CPI",
        help="Last Update Date",
    )
    fred_series_cpi = fields.Char(
        string="FRED series_id CPI (para inflation)",
        default="CPIAUCSL",
    )
    inflation_link = fields.Char(
        string="Link FRED Inflation",
        default="https://fred.stlouisfed.org/series/CPIAUCSL",
    )
    inflation_yoy = fields.Float(
        string="Annual Inflation (%)",
        digits=(16, 4),
        tracking=True,
    )
    inflation_yoy_date = fields.Date(
        string="Update Date Annual Inflation",
    )
    inflation_6m = fields.Float(
        string="Inflation 6M (%)",
        digits=(16, 4),
        tracking=True,
    )
    inflation_6m_date = fields.Date(
        string="Update Date Inflation 6M",
    )
    inflation_mom = fields.Float(
        string="Inflation MoM (%)",
        digits=(16, 4),
        tracking=True,
    )
    inflation_mom_date = fields.Date(
        string="Update Date Inflation MoM",
    )
    unemployment_value = fields.Float(
        string="Unemployment USA (%)",
        tracking=True,
    )
    unemployment_date = fields.Date(
        string="Update Date Unemployment",
        help="Last Update Date",
    )
    fred_series_unrate = fields.Char(
        string="FRED series_id Unemployment Rate",
        default="UNRATE",
    )
    unemployment_link = fields.Char(
        string="Link FRED Unemployment",
        default="https://fred.stlouisfed.org/series/UNRATE",
    )
    interest_rate_value = fields.Float(
        string="Interest Rate USA (%)",
        tracking=True,
    )
    interest_rate_date = fields.Date(
        string="Update Interest Rate",
        help="Last Update Date",
    )
    fred_series_ffr = fields.Char(
        string="FRED series_id Interest Rate (EFFR/FF)",
        default="DFF",
    )
    interest_rate_link = fields.Char(
        string="Link FRED Interest Rate",
        default="https://fred.stlouisfed.org/series/DFF",
    )
    # Exchange Data - Sp500 etc
    sp500_value = fields.Float(
        string="S&P 500",
        tracking=True,
    )
    sp500_date = fields.Date(
        string="Update Date S&P 500",
        help="Last Update Date",
    )
    fred_series_sp500 = fields.Char(
        string="FRED series_id S&P 500",
        default="SP500",
    )
    sp500_link = fields.Char(
        string="Link FRED S&P 500",
        default="https://fred.stlouisfed.org/series/SP500",
    )
    djia_value = fields.Float(
        string="Dow Jones Industrial Average (DJIA)",
        tracking=True,
    )
    djia_date = fields.Date(
        string="Update Date DJIA",
        help="Last Update Date",
    )
    fred_series_djia = fields.Char(
        string="FRED series_id DJIA",
        default="DJIA",
    )
    djia_link = fields.Char(
        string="Link FRED DJIA",
        default="https://fred.stlouisfed.org/series/DJIA",
    )
    nasdaqcom_value = fields.Float(
        string="NASDAQ Composite Index",
        tracking=True,
    )
    nasdaqcom_date = fields.Date(
        string="Update Date NASDAQ Composite",
        help="Last Update Date",
    )
    fred_series_nasdaqcom = fields.Char(
        string="FRED series_id NASDAQ Composite",
        default="NASDAQCOM",
    )
    nasdaqcom_link = fields.Char(
        string="Link FRED NASDAQ Composite",
        default="https://fred.stlouisfed.org/series/NASDAQCOM",
    )
    nasdaq100_value = fields.Float(
        string="NASDAQ 100 Index",
        tracking=True,
    )
    nasdaq100_date = fields.Date(
        string="Update Date NASDAQ 100",
        help="Last Update Date",
    )
    fred_series_nasdaq100 = fields.Char(
        string="FRED series_id NASDAQ 100",
        default="NASDAQ100",
    )
    nasdaq100_link = fields.Char(
        string="Link FRED NASDAQ 100",
        default="https://fred.stlouisfed.org/series/NASDAQ100",
    )

    # Helpers FRED
    def _get_fred_api_key(self):
        api_key = self.env["ir.config_parameter"].sudo().get_param("financial.apy_key")
        if not api_key:
            _logger.error(
                "API key not configured in System Parameters (financial.apy_key)"
            )
            return None
        return api_key

    def _fred_get_observations(self, series_id, api_key, limit=50, sort_order="desc"):
        # Devuelve el payload JSON de FRED observations.
        url = "https://api.stlouisfed.org/fred/series/observations"
        params = {
            "series_id": series_id,
            "api_key": api_key,
            "file_type": "json",
            "sort_order": sort_order,
            "limit": limit,
        }
        r = requests.get(url, params=params, timeout=30)
        r.raise_for_status()
        return r.json()

    def _fred_get_latest_valid(self, series_id, api_key):
        """ Devuelve (date, value_float) para la última observación válida.
        Ignora values '.' o vacíos. """
        if not series_id:
            return (None, None)

        payload = self._fred_get_observations(
            series_id, api_key, limit=50, sort_order="desc"
        )
        obs = payload.get("observations") or []
        for item in obs:
            v = item.get("value")
            d = item.get("date")
            if not d:
                continue
            if v in (None, "", "."):
                continue
            try:
                return (fields.Date.from_string(d), float(v))
            except Exception:
                continue
        return (None, None)

    # Cálculo de inflación anual
    def _compute_inflation_rate(self, series_id_cpi, api_key, periods_back):
        """
        Calcula % cambio desde CPI usando 'periods_back' observaciones hacia atrás.
        Ej:
          periods_back=1  -> MoM (si la serie es mensual)
          periods_back=6  -> 6M
          periods_back=12 -> YoY
        Fórmula: (CPI_t / CPI_(t-periods_back) - 1) * 100
        """
        if not series_id_cpi:
            return (None, None)

        # Necesitamos (periods_back + 1) valores válidos
        need = periods_back + 1
        payload = self._fred_get_observations(
            series_id_cpi, api_key, limit=max(50, need * 3), sort_order="desc"
        )
        obs = payload.get("observations") or []

        vals = []
        for item in obs:
            v = item.get("value")
            d = item.get("date")
            if not d or v in (None, "", "."):
                continue
            try:
                vals.append((fields.Date.from_string(d), float(v)))
            except Exception:
                continue
            if len(vals) >= need:
                break

        if len(vals) < need:
            return (None, None)

        d0, cpi0 = vals[0]
        dN, cpiN = vals[periods_back]
        if not cpiN:
            return (None, None)

        change = round((cpi0 / cpiN - 1.0) * 100.0, 4)
        return (d0, change)

    # Public API (acciones)
    @api.model
    def update_from_fred(self):
        """
        Acción/cron para actualizar indicadores desde FRED.
        Crea 1 registro si no existe.
        """
        api_key = self._get_fred_api_key()
        if not api_key:
            return

        rec = self.search([], limit=1)
        if not rec:
            rec = self.create({"name": "FRED Indicators"})

        try:
            vals = {}

            # TGA
            d, v = rec._fred_get_latest_valid(rec.fred_series_tga, api_key)
            if d:
                vals.update({"tga_date": d, "tga_value": v})

            # Reservas
            d, v = rec._fred_get_latest_valid(rec.fred_series_reserves, api_key)
            if d:
                vals.update({"reserves_date": d, "reserves_value": v})

            # SRF (si hay series_id)
            d, v = rec._fred_get_latest_valid(rec.fred_series_srf, api_key)
            if d:
                vals.update({"srf_date": d, "srf_value": v})

            # ON RRP
            d, v = rec._fred_get_latest_valid(rec.fred_series_on_rrp, api_key)
            if d:
                vals.update({"on_rrp_date": d, "on_rrp_value": v})

            # SOFR
            d, v = rec._fred_get_latest_valid(rec.fred_series_sofr, api_key)
            if d:
                vals.update({"sofr_date": d, "sofr_value": v})

            # BONDS
            d, v = rec._fred_get_latest_valid(rec.fred_series_bonds, api_key)
            if d:
                vals.update({"bonds_date": d, "bonds_usa_value": v})

            # BONDS
            d, v = rec._fred_get_latest_valid(rec.fred_series_inverse_repo, api_key)
            if d:
                vals.update({"inverse_repo_date": d, "inverse_repo_value": v})

            # USD Index (DXY proxy)
            d, v = rec._fred_get_latest_valid(rec.fred_series_usd_index, api_key)
            if d:
                vals.update({"usd_index_date": d, "usd_index_value": v})

            # VIX
            d, v = rec._fred_get_latest_valid(rec.fred_series_vix, api_key)
            if d:
                vals.update({"vix_date": d, "vix_value": v})

            # CPI nivel Inflación Total
            d, v = rec._fred_get_latest_valid(rec.fred_series_cpi, api_key)
            if d:
                vals.update({"inflation_cpi_date": d, "inflation_cpi_value": v})

            # Inflaciones calculadas desde CPI
            # YoY (12 meses)
            dchg, chg = rec._compute_inflation_rate(
                rec.fred_series_cpi, api_key, periods_back=12
            )
            if dchg:
                vals.update({"inflation_yoy_date": dchg, "inflation_yoy": chg})

            # 6M (6 meses)
            dchg, chg = rec._compute_inflation_rate(
                rec.fred_series_cpi, api_key, periods_back=6
            )
            if dchg:
                vals.update({"inflation_6m_date": dchg, "inflation_6m": chg})

            # MoM (1 mes)
            dchg, chg = rec._compute_inflation_rate(
                rec.fred_series_cpi, api_key, periods_back=1
            )
            if dchg:
                vals.update({"inflation_mom_date": dchg, "inflation_mom": chg})

            # Desempleo
            d, v = rec._fred_get_latest_valid(rec.fred_series_unrate, api_key)
            if d:
                vals.update({"unemployment_date": d, "unemployment_value": v})

            # Tipo interés
            d, v = rec._fred_get_latest_valid(rec.fred_series_ffr, api_key)
            if d:
                vals.update({"interest_rate_date": d, "interest_rate_value": v})

            # S&P 500
            d, v = rec._fred_get_latest_valid(rec.fred_series_sp500, api_key)
            if d:
                vals.update({"sp500_date": d, "sp500_value": v})

            # DJIA
            d, v = rec._fred_get_latest_valid(rec.fred_series_djia, api_key)
            if d:
                vals.update({"djia_date": d, "djia_value": v})

            # NASDAQ Composite
            d, v = rec._fred_get_latest_valid(rec.fred_series_nasdaqcom, api_key)
            if d:
                vals.update({"nasdaqcom_date": d, "nasdaqcom_value": v})

            # NASDAQ 100
            d, v = rec._fred_get_latest_valid(rec.fred_series_nasdaq100, api_key)
            if d:
                vals.update({"nasdaq100_date": d, "nasdaq100_value": v})

            # Guardar
            vals.update(
                {
                    "last_sync": fields.Datetime.now(),
                    "last_sync_message": "OK",
                }
            )
            rec.sudo().write(vals)

        except requests.exceptions.RequestException as e:
            _logger.error("FRED connection error: %s", e)
            rec.sudo().write(
                {
                    "last_sync": fields.Datetime.now(),
                    "last_sync_message": f"HTTP error: {e}",
                }
            )
        except Exception as e:
            _logger.exception("Unexpected error syncing FRED indicators: %s", e)
            rec.sudo().write(
                {
                    "last_sync": fields.Datetime.now(),
                    "last_sync_message": f"Unexpected: {e}",
                }
            )

    @api.model
    def cron_update_from_fred(self):
        """Para llamarlos desde Acciones Planificadas o de Servidor."""
        self.update_from_fred()

    threshold_ids = fields.One2many(
        "dashboard.control",
        "indicators_id",
        string="Dashboard thresholds",
    )
