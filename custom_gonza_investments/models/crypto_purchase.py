# Este modelo sirve para almacenar las compras de criptomonedas (FIFO)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class CryptoValuationLayer(models.Model):
    _name = "crypto.valuation.layer"
    _description = "Crypto Valuation (FIFO)"
    _order = "date asc, id asc"
    _check_company_auto = True
    _rec_name = "asset_id"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    asset_id = fields.Many2one(
        "crypto.asset",
        index=True,
        string="Asset",
    )
    company_id = fields.Many2one(
        "res.company",
        required=True,
        default=lambda self: self.env.company.id,
        index=True,
        string="Company",
    )
    date = fields.Datetime(
        required=True,
        default=fields.Datetime.now,
        index=True,
        string="Purchase Date",
    )
    qty_purchase = fields.Float(
        required=True,
        digits="Product Unit of Measure",
        string="Quantity Purchased",
    )
    qty_sold = fields.Float(
        default=0.0,
        digits="Product Unit of Measure",
        string="Quantity Sold",
    )
    qty_available = fields.Float(
        compute="_compute_qty_available",
        store=True,
        string="Quantity Available",
    )
    currency_id = fields.Many2one(
        "res.currency",
        related="company_id.currency_id",
        store=True,
        readonly=True,
        string="Currency",
    )
    unit_cost_eur = fields.Monetary(
        currency_field="currency_id",
        required=True,
        compute="_compute_unit_cost",
        string="Unit Cost (€)",
    )
    fee_eur = fields.Monetary(
        currency_field="currency_id",
        default=0.0,
        string="Total Fee (€)",
    )
    total_cost_eur = fields.Monetary(
        currency_field="currency_id",
        store=True,
        string="Total Cost (€)",
    )
    purchase_mode = fields.Many2one(
        "crypto.purchase.mode",
        string="Purchase Mode",
    )
    bank_document = fields.Binary(
        string="Bank Transfer Document",
    )
    exchange_document = fields.Binary(
        string="Exchange Purchase Document",
    )
    note = fields.Char(
        string="Note",
    )

    _sql_constraints = [
        (
            "qty_purchase_positive",
            "CHECK(qty_purchase > 0)",
            "qty_purchase must be positive.",
        ),
        (
            "qty_sold_not_negative",
            "CHECK(qty_sold >= 0)",
            "qty_sold cannot be negative.",
        ),
        (
            "qty_sold_le_qty_purchase",
            "CHECK(qty_sold <= qty_purchase)",
            "No more can leave than went in.",
        ),
    ]

    # Se ejecuta al crear un nuevo registro para establecer valores por defecto
    @api.model
    def default_get(self, fields_list):
        vals = super().default_get(fields_list)
        if not vals.get("company_id"):
            vals["company_id"] = self.env.company.id
        if "qty_sold" in self._fields and vals.get("qty_sold") is None:
            vals["qty_sold"] = 0.0
        return vals

    # Obliga a seleccionar un Asset
    @api.constrains("asset_id")
    def _check_asset_required(self):
        for crypto in self:
            if not crypto.asset_id:
                raise ValidationError(_("You must select an Asset."))

    # Calcula la cantidad disponible
    @api.depends("qty_purchase", "qty_sold")
    def _compute_qty_available(self):
        for crypto in self:
            crypto.qty_available = crypto.qty_purchase - crypto.qty_sold

    # Calcula el coste unitario en EUR
    @api.depends("qty_purchase", "total_cost_eur", "fee_eur")
    def _compute_unit_cost(self):
        for crypto in self:
            if crypto.qty_purchase:
                crypto.unit_cost_eur = (crypto.total_cost_eur / crypto.qty_purchase) + (
                    crypto.fee_eur or 0.0
                )
            else:
                crypto.unit_cost_eur = 0.0

    # Si cambias de moneda en el asset, actualiza la compañía
    @api.onchange("asset_id")
    def _onchange_asset(self):
        # Sólo sincroniza compañía; la moneda se hereda por related desde company_id
        for crypto in self:
            if (
                crypto.asset_id
                and crypto.asset_id.company_id
                and crypto.company_id != crypto.asset_id.company_id
            ):
                crypto.company_id = crypto.asset_id.company_id.id

    # Acción para abrir las asignaciones de venta relacionadas
    def action_open_allocations(self):
        self.ensure_one()
        action = self.env.ref(
            "custom_gonza_investments.action_crypto_allocation"
        ).read()[0]
        action["domain"] = [("in_layer_id", "=", self.id)]
        return action
