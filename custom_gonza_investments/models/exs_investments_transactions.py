from odoo import models, fields, api
from collections import defaultdict


class InvestmentTransactions(models.Model):
    _name = 'inv.investments.transactions'
    _description = 'Transaction Model'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "investment_name"

    # Nombre de la cripto
    investment_name = fields.Many2one(
        comodel_name="inv.investment.assets",
        string="Name",
        required=True
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
    # Rentabilidad obtenida en porcentaje
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
        comodel_name="inv.investment.purchase.mode",
        string="Buy Mode"
    )
    # Ubicación del activo
    investment_location_id = fields.Many2one(
        comodel_name="inv.investment.location",
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
            totals[investment_name]['purchaseback_price'] += investment.purchaseback_price
            # Incrementa el contador de inversiones para calcular promedios
            totals[investment_name]['count'] += 1

        # Calcula los promedios después de sumar todos los valores
        for investment_name, data in totals.items():
            if data['count'] > 0:
                data['profit_percentage_avg'] = data['profit_percentage_sum'] / data[
                    'count']

        return totals
