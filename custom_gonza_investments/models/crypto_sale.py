# Este modelo sirve para almacenar las ventas de criptomonedas

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class CryptoSale(models.Model):
    _name = "crypto.sale"
    _description = "Crypto Sale"
    _order = "date desc, id desc"
    _check_company_auto = True
    _rec_name = "asset_id"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    asset_id = fields.Many2one(
        "crypto.asset",
        required=True,
        string="Asset",
    )
    date = fields.Datetime(
        required=True,
        default=fields.Datetime.now,
        string="Sale Date",
    )
    company_id = fields.Many2one(
        "res.company",
        required=True,
        default=lambda self: self.env.company,
        string="Company",
    )
    line_ids = fields.One2many(
        "crypto.sale.line",
        "sale_id",
        string="Lines",
    )
    state = fields.Selection(
        [("draft", "Draft"), ("confirmed", "Confirmed"), ("cancel", "Canceled")],
        default="draft",
        string="Status",
    )
    total_profit_eur = fields.Monetary(
        compute="_compute_totals",
        currency_field="currency_id",
        store=True,
        string="Total Profit (€)",
    )
    total_tax_eur = fields.Monetary(
        compute="_compute_totals",
        currency_field="currency_id",
        store=True,
        string="Total Tax (€)",
    )
    currency_id = fields.Many2one(
        "res.currency",
        default=lambda self: self.env.ref("base.EUR"),
        string="Currency",
    )

    @api.depends("line_ids.profit_eur", "line_ids.tax_eur")
    def _compute_totals(self):
        for crypto in self:
            crypto.total_profit_eur = sum(crypto.line_ids.mapped("profit_eur"))
            crypto.total_tax_eur = sum(crypto.line_ids.mapped("tax_eur"))

    def action_confirm(self):
        for sale in self:
            if sale.state != "draft":
                continue
            for line in sale.line_ids:
                line.allocate_fifo()  # aquí ya se crean asignaciones reales
            sale.state = "confirmed"

    def action_cancel(self):
        for sale in self:
            if sale.state != "confirmed":
                continue
            sale.line_ids.mapped(
                "allocation_ids"
            ).unlink()  # esto revertirá qty_sold en metodo unlink
            sale.state = "cancel"

    def unlink(self):
        # Antes de borrar, aseguramos que las ventas confirmadas se cancelan
        # para que se borren allocations y se devuelva qty_sold.
        confirmed_sales = self.filtered(lambda s: s.state == "confirmed")
        if confirmed_sales:
            confirmed_sales.action_cancel()
        return super().unlink()


class CryptoSaleLine(models.Model):
    _name = "crypto.sale.line"
    _description = "Crypto Sale Line"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    sale_id = fields.Many2one(
        "crypto.sale",
        required=True,
        string="Sale"
    )
    asset_id = fields.Many2one(
        "crypto.asset",
        required=True,
        string="Asset",
    )
    qty = fields.Float(
        required=True,
        digits="Product Unit of Measure",
        string="Quantity",
    )
    price_unit_eur = fields.Monetary(
        required=True,
        currency_field="currency_id",
        string="Unit Sale Price (€)",
    )  # precio de venta unitario EUR
    fee_eur = fields.Monetary(
        currency_field="currency_id",
        default=0.0,
        string="Total Fee (€)",
    )  # fee total de esta línea
    company_id = fields.Many2one(
        related="sale_id.company_id",
        store=True,
        string="Company",
    )
    currency_id = fields.Many2one(
        related="sale_id.currency_id",
        store=True,
        string="Currency",
    )
    allocation_ids = fields.One2many(
        "crypto.sale.allocation",
        "sale_line_id",
        string="Allocations FIFO",
    )
    profit_eur = fields.Monetary(
        compute="_compute_profit",
        currency_field="currency_id",
        store=True,
        string="Profit (€)",
    )
    tax_eur = fields.Monetary(
        compute="_compute_profit",
        currency_field="currency_id",
        store=True,
        string="Tax (€)",
    )

    @api.depends(
        "allocation_ids.profit_eur",
        "sale_id.state",
        "qty",
        "price_unit_eur",
        "fee_eur",
    )
    def _compute_profit(self):
        Allocation = self.env["crypto.sale.allocation"]
        for line in self:
            if line.sale_id.state == "confirmed":
                # 1) Beneficio total = suma de allocations
                total_profit = sum(line.allocation_ids.mapped("profit_eur"))
                line.profit_eur = total_profit

                # 2) Impuesto calculado UNA sola vez sobre el beneficio total
                line.tax_eur = Allocation._compute_tax_fifo(total_profit)

                # (Opcional) si no usas tax_eur en cada allocation, no pasa nada.
            else:
                # En borrador (o cancel), simulamos FIFO sin tocar nada en BD
                profit, tax = line._simulate_fifo()
                line.profit_eur = profit
                line.tax_eur = tax

    # Se usa en borrador para simular FIFO sin crear allocations
    def _simulate_fifo(self):
        # Simula el FIFO para calcular beneficio/impuesto SIN crear allocations ni tocar qty_sold.
        self.ensure_one()

        qty_to_sell = self.qty or 0.0
        # Si no hay cantidad o falta contexto básico, no simulamos nada
        if qty_to_sell <= 0 or not self.asset_id or not self.company_id:
            return 0.0, 0.0

        fee_per_unit = (self.fee_eur or 0.0) / qty_to_sell if qty_to_sell else 0.0

        # NO ponemos FOR UPDATE porque sólo es simulación
        self.env.cr.execute(
            """
            SELECT id
            FROM crypto_valuation_layer
            WHERE company_id = %s
              AND asset_id = %s
              AND qty_purchase > qty_sold
            ORDER BY date ASC, id ASC
            """,
            (self.company_id.id, self.asset_id.id),
        )
        # Líneas de compra disponibles:
        pucharse_ids = [row[0] for row in self.env.cr.fetchall()]
        pucharse_lines = self.env["crypto.valuation.layer"].browse(pucharse_ids)

        remaining = qty_to_sell
        total_proceeds = 0.0
        total_cost = 0.0
        total_fee = 0.0

        # Layer sería la línea de compra (traducido: Capa de compra)
        for layer in pucharse_lines:
            if remaining <= 0:
                break

            qty_available = max(layer.qty_purchase - layer.qty_sold, 0.0)
            if qty_available <= 0:
                continue

            take = min(qty_available, remaining)

            total_proceeds += take * self.price_unit_eur
            total_cost += take * layer.unit_cost_eur
            total_fee += take * fee_per_unit
            remaining -= take

        # IMPORTANTE: en simulación NO lanzamos UserError. Lo comento por bug
        # Si falta disponibilidad, simplemente calculamos sobre lo que haya.
        if remaining > 1e-12:
            # _logger.warning(
            #     "SIM FIFO shortage for line %s: wanted %s, missing %s",
            #     self.id, qty_to_sell, remaining
            # )
            pass

        profit = total_proceeds - total_cost - total_fee

        Allocation = self.env["crypto.sale.allocation"]
        tax = Allocation._compute_tax_fifo(profit)

        return profit, tax

    # Se usa en confirmación para crear asignaciones reales
    def allocate_fifo(self):
        # Asignar FIFO consumiendo compras disponibles
        self.ensure_one()
        qty_to_sell = self.qty  # cantidad a vender
        if qty_to_sell <= 0:
            raise UserError(_("The quantity to be sold must be positive."))

        # Opcional: prorrateo de fees por unidad según la cantidad total vendida
        fee_per_unit = (self.fee_eur or 0.0) / qty_to_sell

        # Lock preventivo para concurrencia (usa SQL para FOR UPDATE)
        self.env.cr.execute(
            """
            SELECT id FROM crypto_valuation_layer
            WHERE company_id = %s AND asset_id = %s AND qty_purchase > qty_sold
            ORDER BY date ASC, id ASC
            FOR UPDATE
        """,
            (self.company_id.id, self.asset_id.id),
        )
        # Líneas de compra disponibles:
        pucharse_ids = [row[0] for row in self.env.cr.fetchall()]
        pucharse_lines = self.env["crypto.valuation.layer"].browse(pucharse_ids)

        allocations = []
        remaining = qty_to_sell
        for layer in pucharse_lines:
            if remaining <= 0:
                break
            take = min(
                layer.qty_available, remaining
            )  # Cantidad a tomar de esta compra
            if take <= 0:
                continue
            # Registrar asignación
            alloc = self.env["crypto.sale.allocation"].create(
                {
                    "sale_line_id": self.id,
                    "in_layer_id": layer.id,
                    "qty_sold": take,
                    "unit_cost_eur": layer.unit_cost_eur,
                    "proceeds_unit_eur": self.price_unit_eur,
                    "fee_unit_eur": fee_per_unit,
                    "date": self.sale_id.date,
                }
            )
            allocations.append(alloc)
            # Actualizar compra (qty_sold)
            layer.qty_sold += take
            remaining -= take

        # Error si no se ha podido vender toda la cantidad (por falta de tokens)
        if remaining > 1e-12:
            raise UserError(
                _("There is not enough availability to sell %s %s. %s are missing.")
                % (self.qty, self.asset_id.symbol, remaining)
            )

        # recomputa campos dependientes
        self.invalidate_recordset(["allocation_ids", "profit_eur", "tax_eur"])

    def unlink(self):
        # Borramos primero las allocations vía ORM
        # para que se ejecute CryptoSaleAllocation.unlink() y se devuelva qty_sold.
        self.mapped("allocation_ids").unlink()
        return super().unlink()
