from odoo import models, fields, api
from collections import defaultdict


class InvestmentTransactions(models.Model):
    _name = 'investments.transactions'
    _description = 'Transaction Model'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "investment_name"

    # Nombre de la cripto
    investment_name = fields.Many2one(
        comodel_name="investment.assets",
        string="Name",
        required=True
    )
    # Tipo de Operación
    transaction_type = fields.Selection(
        [("buy", "Buy"), ("sell", "Sell")],
        string="Transaction Type",
        required=True,
        default="buy",
    )
    #Cantidad comprada en FIAT
    quantity_in_fiat = fields.Float(
        string="Quantity Buy in FIAT money",
        required=True
    )
    # Cantidad comprada de moneda cripto
    quantity_in_crypto = fields.Float(
        string="Quantity Buy in Crypto money",
        required=True,
        digits=(16, 8)
    )
    # Precio de compra unitario
    transaction_price = fields.Float(
        string="Purchase Price",
        compute="_compute_investment_metrics",
        store=True
    )
    # Precio actual unitario
    current_price = fields.Float(
        string="Current Unit Price",
        related="investment_name.current_price",
        required=True
    )
    # Tipo de activo
    investment_asset_type = fields.Selection(
        string="Asset Type",
        related="investment_name.asset_type",
        required=True
    )
    # Precio actual del total de la inversión
    current_investment_price = fields.Float(
        string="Current Investment Price",
        compute="_compute_investment_metrics",
        store=True
    )
    # Diferencia entre el precio actual unitario y el precio de compra unitario
    price_difference = fields.Float(
        string="Price Difference",
        compute="_compute_investment_metrics",
        store=True
    )
    # Rentabilidad obtenida en metálico
    profit = fields.Float(
        string="Profit",
        compute="_compute_investment_metrics",
        store=True
    )
    # Rentabilidad obtenida en porcentaje
    profit_percentage = fields.Float(
        string="Profit Percentage",
        compute="_compute_investment_metrics",
        store=True)
    # Total a pagar en impuestos
    tax_quantity = fields.Float(
        string="Total Tax",
        compute="_compute_investment_metrics",
        store=True
    )
    # Rentabilidad neta luego de impuestos
    profit_net = fields.Float(
        string="Net Profit",
        compute="_compute_investment_metrics",
        store=True
    )
    # Precio de recompra unitario
    purchaseback_price = fields.Float(
        string="Purchase Back Price",
        compute="_compute_investment_metrics",
        store=True
    )
    description = fields.Text(
        string="Description"
    )
    date = fields.Date(
        string="Date",
        required=True
    )
    # Modo de compra
    investment_purchase_mode_id = fields.Many2one(
        comodel_name="investment.purchase.mode",
        string="Buy Mode"
    )
    # Ubicación del activo
    investment_location_id = fields.Many2one(
        comodel_name="investment.location",
        string="Investment location"
    )
    # Status del activo
    status = fields.Selection(
        selection=[
            ('in_portfolio', 'In portfolio'),
            ('sold', 'Sold')],
        string="Status"
    )
    # Estrategia de la inversión
    strategy = fields.Selection(
        selection=[
            ('trading', 'Trading'),
            ('holding', 'Holding')],
        string="Strategy",
        default='holding'
    )
    # Relaciona con las líneas de venta para FIFO
    sale_lines = fields.One2many(
        "investment.transaction.sale.line", "sale_transaction_id", string="Related Buys"
    )

    @api.depends('transaction_price', 'current_price', 'quantity_in_crypto',
                 'quantity_in_fiat')
    def _compute_investment_metrics(self):
        for record in self:
            if record.investment_asset_type in ['crypto', 'actions', 'bonds', 'funds']:
                # Calcula diferencias de precio y ganancias
                if record.quantity_in_fiat and record.quantity_in_crypto:
                    record.transaction_price = record.quantity_in_fiat / record.quantity_in_crypto
                else:
                    record.transaction_price = 0

                if record.transaction_price and record.current_price:
                    record.price_difference = record.current_price - record.transaction_price
                    record.current_investment_price = record.quantity_in_crypto * record.current_price
                    record.profit = record.current_investment_price - record.quantity_in_fiat
                else:
                    record.price_difference = 0
                    record.current_investment_price = 0
                    record.profit = 0

                # Calcula porcentaje de ganancia
                if record.transaction_price:
                    record.profit_percentage = (
                                                   record.price_difference / record.transaction_price) * 100 if record.price_difference else 0
                else:
                    record.profit_percentage = 0

                # Calcula impuestos y ganancia neta
                record.tax_quantity = record._calculate_tax(record.profit)
                record.profit_net = record.profit - record.tax_quantity if record.profit else 0

                # Calcula precio de recompra
                if record.current_investment_price and record.quantity_in_crypto:
                    record.purchaseback_price = (
                        (
                            record.current_investment_price - record.tax_quantity) / record.quantity_in_crypto
                    )
                else:
                    record.purchaseback_price = 0
            else:
                record.quantity_in_crypto = 1
                record.transaction_price = record.quantity_in_fiat
                record.price_difference = 0
                record.profit = 0
                record.profit_percentage = 0
                record.tax_quantity = 0
                record.profit_net = 0
                record.purchaseback_price = 0

    def _calculate_tax(self, profit):
        if profit <= 6000:
            return profit * 0.19
        elif profit <= 50000:
            return 6000 * 0.19 + (profit - 6000) * 0.21
        elif profit <= 200000:
            return 6000 * 0.19 + (50000 - 6000) * 0.21 + (profit - 50000) * 0.23
        else:
            return 6000 * 0.19 + (50000 - 6000) * 0.21 + (200000 - 50000) * 0.23 + (
                    profit - 200000) * 0.26

    # Mostrar datos en modelo de totales
    @api.model
    def get_investment_totals(self):
        """
        Calcula los totales de inversiones agrupados por el campo `investment_name.custom_name`.
        Retorna un diccionario con la suma de los campos relevantes y calcula promedios donde sea necesario.
        """
        investments = self.search([])

        # Diccionario para almacenar los totales por nombre
        totals = defaultdict(lambda: {
            'quantity_in_fiat': 0.0,
            'quantity_in_crypto': 0.0,
            'profit': 0.0,
            'profit_net': 0.0,
            'profit_percentage_sum': 0.0,  # Suma para calcular el promedio
            'profit_percentage_avg': 0.0,  # Promedio final
            'current_investment_price': 0.0,
            'price_difference': 0.0,
            'tax_quantity': 0.0,
            'purchaseback_price': 0.0,
            'investment_asset_type': investment.investment_asset_type,
            'count': 0  # Contador para promedios
        })

        # Itera sobre las inversiones para acumular los valores
        for investment in investments:
            investment_name = investment.investment_name.custom_name
            totals[investment_name]['quantity_in_fiat'] += investment.quantity_in_fiat
            totals[investment_name]['quantity_in_crypto'] += investment.quantity_in_crypto
            totals[investment_name]['profit'] += investment.profit
            totals[investment_name]['profit_net'] += investment.profit_net
            totals[investment_name]['profit_percentage_sum'] += investment.profit_percentage
            totals[investment_name]['current_investment_price'] += investment.current_investment_price
            totals[investment_name]['price_difference'] += investment.price_difference
            totals[investment_name]['tax_quantity'] += investment.tax_quantity
            totals[investment_name]["investment_asset_type"] = (
                investment.investment_asset_type
            )
            totals[investment_name]['purchaseback_price'] += investment.purchaseback_price
            # Incrementa el contador de inversiones para calcular promedios
            totals[investment_name]['count'] += 1

        # Calcula los promedios después de sumar todos los valores
        for investment_name, data in totals.items():
            if data['count'] > 0:
                data['profit_percentage_avg'] = data['profit_percentage_sum'] / data[
                    'count']

        return totals

    def _apply_fifo_matching(self):
        """
        Solo se llama para transacciones de venta.
        Recorre las compras anteriores disponibles (status=in_portfolio) usando FIFO
        y crea líneas de relación con la cantidad usada.
        """
        for sale in self:
            if sale.transaction_type != 'sell':
                continue

            remaining_qty = sale.quantity_in_crypto

            # Buscamos compras anteriores para la misma cripto, en portafolio y no usadas del todo
            buy_transactions = self.search([
                ('transaction_type', '=', 'buy'),
                ('investment_name', '=', sale.investment_name.id),
                ('status', '=', 'in_portfolio'),
                ('quantity_in_crypto', '>', 0),
            ], order='date asc')

            for buy in buy_transactions:
                if remaining_qty <= 0:
                    break

                # Ver cuánto queda disponible de esta compra (usado en otras ventas)
                used_qty = sum(self.env['investment.transaction.sale.line'].search([
                    ('buy_transaction_id', '=', buy.id)
                ]).mapped('quantity_used'))

                available_qty = buy.quantity_in_crypto - used_qty
                if available_qty <= 0:
                    continue

                qty_to_use = min(available_qty, remaining_qty)

                self.env['investment.transaction.sale.line'].create({
                    'sale_transaction_id': sale.id,
                    'buy_transaction_id': buy.id,
                    'quantity_used': qty_to_use,
                })

                remaining_qty -= qty_to_use

    def create(self, vals):
        record = super().create(vals)
        if record.transaction_type == "sell":
            record._apply_fifo_matching()
        return record
