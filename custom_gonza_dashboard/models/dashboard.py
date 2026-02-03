from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class DashboardControl(models.Model):
    _name = "dashboard.control"
    _description = "Dashboard Model"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name = "name"
    _order = "name asc"

    name = fields.Char(
        string="Name",
        required=True,
    )
    indicators_id = fields.Many2one(
        "financial.indicators",
        required=True,
        ondelete="cascade",
    )

    indicator = fields.Selection(
        [
            ("reserves_value", "Bank Reserves"),
            ("srf_value", "SRF USA"),
            ("on_rrp_value", "ON RRP"),
            ("sofr_value", "SOFR USA"),
            ("bonds_usa_value", "Bonds USA"),
            ("inverse_repo_value", "Inverse Repo"),
            ("usd_index_value", "USD Index"),
            ("vix_value", "VIX"),
            ("move_value", "MOVE"),
            ("sp500_value", "S&P 500"),
            ("djia_value", "Dow Jones (DJIA)"),
            ("nasdaqcom_value", "NASDAQ Composite"),
            ("nasdaq100_value", "NASDAQ 100"),
            ("inflation_yoy", "Inflation YoY"),
            ("inflation_6m", "Inflation 6M"),
            ("inflation_mom", "Inflation MoM"),
            ("unemployment_value", "Unemployment"),
            ("interest_rate_value", "Interest Rate"),
        ],
        required=True,
    )

    # 5 valores configurables
    v1 = fields.Float(
        string="V1",
    )
    v2 = fields.Float(
        string="V2",
    )
    v3 = fields.Float(
        string="V3",
    )
    v4 = fields.Float(
        string="V4",
    )
    v5 = fields.Float(
        string="V5",
    )

    higher_is_worse = fields.Boolean(
        string="Higher is worse",
        default=True,
        help="If checked: higher values mean worse color (green to red)."
             "If unchecked: higher values mean better color (red to green)."
    )

    current_value = fields.Float(
        string="Current Value",
        compute="_compute_status",
        store=True,
    )
    level = fields.Selection(
        [
            ("5", "Strong Green"),
            ("4", "Green"),
            ("3", "Yellow"),
            ("2", "Orange"),
            ("1", "Red"),
            ("0", "N/A"),
        ],
        string="Level",
        compute="_compute_status",
        store=True,
    )

    level_class = fields.Char(
        string="CSS Class",
        compute="_compute_status",
        store=True,
    )

    @api.depends(
        "indicator",
        "v1",
        "v2",
        "v3",
        "v4",
        "v5",
        "higher_is_worse",
        "indicators_id.reserves_value",
        "indicators_id.srf_value",
        "indicators_id.on_rrp_value",
        "indicators_id.sofr_value",
        "indicators_id.bonds_usa_value",
        "indicators_id.inverse_repo_value",
        "indicators_id.usd_index_value",
        "indicators_id.vix_value",
        "indicators_id.move_value",
        "indicators_id.sp500_value",
        "indicators_id.djia_value",
        "indicators_id.nasdaqcom_value",
        "indicators_id.nasdaq100_value",
        "indicators_id.inflation_yoy",
        "indicators_id.inflation_6m",
        "indicators_id.inflation_mom",
        "indicators_id.unemployment_value",
        "indicators_id.interest_rate_value",
    )
    def _compute_status(self):
        for rec in self:
            # Defaults seguros
            rec.current_value = 0.0
            rec.level = "0"
            rec.level_class = "fi_level_0"

            # Sin indicador o sin registro de indicadores: N/A
            if not rec.indicator or not rec.indicators_id:
                continue

            # Leer valor del campo seleccionado; si es falsy, usar 0.0
            value = rec.indicators_id[rec.indicator]
            if value is None:
                continue  # N/A si el campo está realmente vacío

            rec.current_value = float(value)

            # Validación de umbrales (aquí decide el criterio)
            cuts = [rec.v1, rec.v2, rec.v3, rec.v4, rec.v5]

            # Si no están configurados, N/A (elige una regla: por ejemplo exigir que v5 != 0 y orden)
            if not rec.v5 or not (rec.v1 <= rec.v2 <= rec.v3 <= rec.v4 <= rec.v5):
                continue

            # Cálculo
            if rec.current_value < rec.v2:
                lvl = 5
            elif rec.current_value < rec.v3:
                lvl = 4
            elif rec.current_value < rec.v4:
                lvl = 3
            elif rec.current_value < rec.v5:
                lvl = 2
            else:
                lvl = 1

            if not rec.higher_is_worse:
                lvl = 6 - lvl

            rec.level = str(lvl)
            rec.level_class = f"fi_level_{lvl}"
