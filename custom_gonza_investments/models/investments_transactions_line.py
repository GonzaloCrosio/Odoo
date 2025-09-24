from odoo import models, fields, api
from collections import defaultdict
from odoo.exceptions import ValidationError


class InvestmentTransactionLine(models.Model):
    _name = 'investment.transaction.line'
    _description = 'Line Transaction Model'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "investment_name_line"

    investment_name_line = fields.Many2one(
        related="transaction_id.investment_name",
        string="Investment Name",
        required=True
    )
    transaction_id = fields.Many2one(
        comodel_name='investment.transaction',
        string="Investment Transaction",
        ondelete='cascade',
        readonly=True,
    )
    # Cantidad comprada en FIAT
    quantity_in_fiat = fields.Float(
        string="Quantity in FIAT money",
        required=True
    )
    # Cantidad comprada de moneda cripto
    quantity_in_crypto = fields.Float(
        string="Quantity in Crypto money",
        required=True,
        digits=(16, 8)
    )
    # Precio de transacción unitario
    transaction_price = fields.Float(
        string="Transaction Price",
        compute="_compute_investment_metrics",
        store=True
    )
    # Precio actual unitario
    current_price = fields.Float(
        string="Current Unit Price",
        related="transaction_id.investment_name.current_price",
        required=True
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
    type = fields.Selection(
        selection=[('purchase', 'Purchase'), ('sale', 'Sale')],
        string="Transaction Type",
        required=True
    )
    # Tipo de activo
    investment_asset_type = fields.Selection(
        string="Asset Type",
        related="transaction_id.investment_name.asset_type",
        required=True
    )

    @api.depends('transaction_price', 'current_price', 'quantity_in_crypto',
                 'quantity_in_fiat', 'type')
    def _compute_investment_metrics(self):
        for record in self:
            # Buscar la línea de purchase dentro de la misma transacción
            purchase_line = record.transaction_id.transaction_line_ids.filtered(
                lambda l: l.type == 'purchase')

            # Si hay una línea de purchase, tomar sus valores de referencia
            purchase_price = purchase_line.transaction_price if purchase_line else 0
            purchase_quantity_fiat = purchase_line.quantity_in_fiat if purchase_line else 0

            if record.type == 'purchase':
                if record.quantity_in_fiat and record.quantity_in_crypto:
                    record.transaction_price = record.quantity_in_fiat / record.quantity_in_crypto
                else:
                    record.transaction_price = 0

                if record.transaction_price and record.current_price:
                    record.price_difference = record.current_price - record.transaction_price
                    record.current_price = record.quantity_in_crypto * record.current_price
                    record.profit = record.current_price - record.quantity_in_fiat
                else:
                    record.price_difference = 0
                    record.current_price = 0
                    record.profit = 0

                if record.transaction_price:
                    record.profit_percentage = (
                                                       record.price_difference / record.transaction_price) * 100 if record.price_difference else 0
                else:
                    record.profit_percentage = 0

                record.tax_quantity = record._calculate_tax(record.profit)
                record.profit_net = record.profit - record.tax_quantity if record.profit else 0

                if record.current_price and record.quantity_in_crypto:
                    record.purchaseback_price = ((
                                                         record.current_price - record.tax_quantity) / record.quantity_in_crypto)
                else:
                    record.purchaseback_price = 0

            elif record.type == 'sale':
                if record.quantity_in_fiat and record.quantity_in_crypto:
                    record.transaction_price = record.quantity_in_fiat / record.quantity_in_crypto
                else:
                    record.transaction_price = 0

                if purchase_price:  # Usamos el transaction_price de la línea de purchase como referencia
                    record.price_difference = record.transaction_price - purchase_price
                else:
                    record.price_difference = 0

                if record.transaction_price and record.current_price:
                    record.current_price = record.quantity_in_crypto * record.current_price
                    record.profit = record.current_price - purchase_quantity_fiat
                else:
                    record.current_price = 0
                    record.profit = 0

                if purchase_price:
                    record.profit_percentage = (
                                                       record.price_difference / purchase_price) * 100 if record.price_difference else 0
                else:
                    record.profit_percentage = 0

                record.tax_quantity = record._calculate_tax(record.profit)
                record.profit_net = record.profit - record.tax_quantity if record.profit else 0

                if record.current_price and record.quantity_in_crypto:
                    record.purchaseback_price = ((
                                                         record.current_price - record.tax_quantity) / record.quantity_in_crypto)
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
        Calcula los totales de inversiones agrupados por transacción,
        restando correctamente el FIAT basado en el precio de compra original en ventas.
        """
        investments = self.search([])

        # Diccionario para almacenar los totales por transacción
        totals = defaultdict(lambda: {
            'quantity_in_fiat': 0.0,
            'quantity_in_crypto': 0.0,
            'profit': 0.0,
            'profit_net': 0.0,
            'profit_percentage_sum': 0.0,
            'profit_percentage_avg': 0.0,
            'current_price': 0.0,
            'price_difference': 0.0,
            'tax_quantity': 0.0,
            'purchaseback_price': 0.0,
            'investment_asset_type': '',
            'count': 0,
            'transaction_price': 0.0  # Guardamos el precio de compra original
        })

        # Iterar sobre las inversiones para calcular totales
        for investment in investments:
            transaction_id = investment.transaction_id.display_name

            # Si la transacción no existe en el diccionario, la inicializamos
            if transaction_id not in totals:
                totals[transaction_id][
                    'investment_asset_type'] = investment.investment_asset_type

            # Guardar el precio de compra si es una línea de tipo 'purchase'
            if investment.type == 'purchase':
                totals[transaction_id]['transaction_price'] = investment.transaction_price

            # Procesar los valores de las transacciones
            if investment.type == 'purchase':
                totals[transaction_id][
                    'quantity_in_crypto'] += investment.quantity_in_crypto
                totals[transaction_id][
                    'quantity_in_fiat'] += investment.quantity_in_fiat
            elif investment.type == 'sale':
                totals[transaction_id][
                    'quantity_in_crypto'] -= investment.quantity_in_crypto
                # Restar el FIAT con base en el precio de compra original
                totals[transaction_id]['quantity_in_fiat'] -= (
                    investment.quantity_in_crypto * totals[transaction_id][
                    'transaction_price']
                )

            # Acumular otros valores relevantes
            totals[transaction_id]['profit'] += investment.profit
            totals[transaction_id]['profit_net'] += investment.profit_net
            totals[transaction_id][
                'profit_percentage_sum'] += investment.profit_percentage
            totals[transaction_id]['current_price'] += investment.current_price
            totals[transaction_id]['price_difference'] += investment.price_difference
            totals[transaction_id]['tax_quantity'] += investment.tax_quantity
            totals[transaction_id][
                'purchaseback_price'] += investment.purchaseback_price

            # Contador de inversiones para calcular promedios
            totals[transaction_id]['count'] += 1

        # Calcular los promedios después de sumar todos los valores
        for transaction_id, data in totals.items():
            if data['count'] > 0:
                data['profit_percentage_avg'] = data['profit_percentage_sum'] / data[
                    'count']

        return totals

    # Validación para evitar que se venda más de lo que se ha comprado
    @api.constrains('quantity_in_crypto', 'type', 'transaction_id')
    def _check_crypto_sale_not_exceed_purchase(self):
        for record in self:
            if record.type == 'sale':
                # Obtener las sumas de purchase y sale en la misma transacción
                totals = self.read_group(
                    [('transaction_id', '=', record.transaction_id.id)],
                    ['quantity_in_crypto', 'type'],
                    ['type']
                )

                # Extraer valores de total comprado y total vendido
                total_purchased = sum(
                    t['quantity_in_crypto'] for t in totals if
                    t['type'] == 'purchase')
                total_sold = sum(t['quantity_in_crypto'] for t in totals if
                                 t['type'] == 'sale')

                # Lanzar error si lo vendido supera lo comprado
                if total_sold > total_purchased:
                    raise ValidationError(
                        f"No puedes vender más ({total_sold}) de lo que has comprado ({total_purchased}) en la transacción {record.transaction_id.display_name}."
                    )

    # Validación para evitar que haya más de una línea de compra por transacción
    @api.constrains('type', 'investment_name_line')
    def _check_unique_purchase_line(self):
        for record in self:
            if record.type == 'purchase':
                # Contar cuántas líneas de compra existen para esta transacción
                purchase_count = self.search_count([
                    ('investment_name_line', '=', record.investment_name_line.id),
                    ('type', '=', 'purchase')
                ])

                # Si hay más de una línea de compra, lanzar error
                if purchase_count > 1:
                    raise ValidationError(
                        f"Solo puede existir una línea de compra en la transacción {record.investment_name_line.display_name}."
                    )
