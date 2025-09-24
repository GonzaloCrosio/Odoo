from odoo import models, fields, api

class InvestmentTotal(models.Model):
    _name = 'investment.total'
    _description = 'Total Investment Data'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    name = fields.Char(
        string="Investment Name"
    )
    total_quantity_in_fiat = fields.Float(
        string="Total Quantity in FIAT"
    )
    total_quantity_in_crypto = fields.Float(
        string="Total Quantity in Crypto",
        digits=(16, 8)
    )
    total_profit = fields.Float(
        string="Total Profit"
    )
    total_profit_net = fields.Float(
        string="Total Net Profit"
    )
    total_current_investment_price = fields.Float(
        string="Total Current Investment Price"
    )
    total_profit_percentage = fields.Float(
        string="Total Profit Percentage"
    )
    total_price_difference = fields.Float(
        string="Total Price Difference",
        compute="_compute_total_difference",
    )
    total_tax_quantity = fields.Float(
        string="Total Tax Quantity"
    )
    total_purchaseback_price = fields.Float(
        string="Total Purchaseback Price",
        compute="_compute_total_difference",
    )
    current_total_participation = fields.Float(
        string="Total Current Participation (%)",
        compute="_compute_total_participation",
        digits=(16, 2)
    )
    fiat_total_participation = fields.Float(
        string="Total FIAT Participation (%)",
        compute="_compute_total_participation",
        digits=(16, 2)
    )
    average_transaction_price = fields.Float(
        string="Average Purchase Price",
        digits=(16, 2),
        compute="_compute_total_difference"
    )
    current_price = fields.Float(
        string="Current Unit Price",
    )

    @api.model
    def create_or_update_total_data(self):
        """
        Actualiza o crea registros en el modelo con los datos agrupados.
        """
        # Obtener los datos agregados
        investment_model = self.env['investment.transaction.line']
        total_data = investment_model.get_investment_totals()

        for custom_name, data in total_data.items():
            # Buscar si el registro ya existe
            existing_record = self.search([('name', '=', custom_name)], limit=1)

            values = {
                'name': custom_name,
                'total_quantity_in_fiat': data['quantity_in_fiat'],
                'total_quantity_in_crypto': data[
                    'quantity_in_crypto'],
                'total_profit': data['profit'],
                'total_profit_net': data['profit_net'],
                'total_current_investment_price': data['current_price'],
                'total_profit_percentage': data['profit_percentage_avg'],
                'total_tax_quantity': data['tax_quantity'],
                'total_purchaseback_price': data['purchaseback_price'],
            }

            if existing_record:
                # Actualizar registro existente
                existing_record.write(values)
            else:
                # Crear nuevo registro si no existe
                self.create(values)

    @api.model
    def open_grouped_investments(self):
        """
        Metodo para crear datos agrupados y abrir la vista
        """
        self.create_or_update_total_data()

        # Retornar la acción asociada a la vista
        return {
            'type': 'ir.actions.act_window',
            'name': 'Total Investments',
            'res_model': 'investment.total',
            'view_mode': 'tree,form,graph,pivot',
            'target': 'current',
        }

    @api.depends('total_current_investment_price', 'total_quantity_in_fiat')
    def _compute_total_participation(self):
        """
        Calcula el porcentaje de participación para cada inversión.
        """
        # Obtener todas las líneas del modelo actual
        all_lines = self.search([])
        # Calcular la suma total de todas las inversiones
        total_investment_price = sum(line.total_current_investment_price
                                     for line in all_lines)
        fiat_investment_price = sum(line.total_quantity_in_fiat
                                    for line in all_lines)

        # Evitar división por cero
        if total_investment_price > 0:
            for line in self:
                line.current_total_participation = (line.total_current_investment_price / total_investment_price) * 100
                line.fiat_total_participation = (line.total_quantity_in_fiat / fiat_investment_price) * 100

        else:
            for line in self:
                line.current_total_participation = 0
                line.fiat_total_participation = 0

    @api.depends('total_current_investment_price', 'total_quantity_in_fiat', 'total_quantity_in_crypto')
    def _compute_total_difference(self):
        # Calcula la diferencia de precio total
        for record in self:
            if record.total_quantity_in_fiat and record.total_quantity_in_crypto and record.total_current_investment_price:
                record.total_price_difference = (record.total_current_investment_price - record.total_quantity_in_fiat) / record.total_quantity_in_crypto
            else:
                record.total_price_difference = 0

            if record.total_current_investment_price and record.total_quantity_in_crypto and record.total_tax_quantity:
                record.total_purchaseback_price = (record.total_current_investment_price - record.total_tax_quantity) / record.total_quantity_in_crypto
            else:
                record.total_purchaseback_price = 0

            if record.total_quantity_in_fiat and record.total_quantity_in_crypto:
                record.average_transaction_price = record.total_quantity_in_crypto / record.total_quantity_in_fiat
            else:
                record.average_transaction_price = 0
