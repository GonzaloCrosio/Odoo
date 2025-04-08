from odoo import models, fields, api, _
from datetime import timedelta
from dateutil.relativedelta import relativedelta


class Loan(models.Model):
    _name = 'loan.loan'
    _description = 'Loan Model'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "name"

    name = fields.Char(
        string="Name",
        required=True,
    )
    amount = fields.Float(
        string="Amount",
        required=True,
    )
    description = fields.Text(
        string="Description",
    )
    date = fields.Date(
        string="Date",
        required=True,
    )
    interest_rate = fields.Float(
        string="Interest Rate (%)",
        required=True,
        help="Nominal annual interest rate."
    )
    term = fields.Integer(
        string="Term in months",
        required=True,
    )
    detail_ids = fields.One2many(
        comodel_name='loan.details',
        inverse_name='loan_id',
        string="Details"
    )
    effective_interest_rate = fields.Float(
        string="Effective Interest Rate Monthly",
        compute="_compute_effective_interest_rate",
        store=True,
        help="Effective monthly interest rate calculated from the nominal annual rate."
    )
    other_day_payment = fields.Boolean(
        string="Signing day first pay day",
    )
    current_debt = fields.Float(
        string="Current Debt",
        compute="_compute_current_debt",
        store=True,
        help="Capital remaining from the last paid installment."
    )
    number = fields.Integer(
        string="Fees paid",
    )
    percentage_debt = fields.Float(
        string="Percentage Debt",
        compute="_compute_percentage_debt",
        store=True,
    )
    number_payments = fields.Integer(
        string="Pending Payments",
        compute="_compute_number_payments",
        store=True,
    )

    # Cálculo del número de pagos pendientes
    @api.depends('number', 'term')
    def _compute_number_payments(self):
        for record in self:
            record.number_payments = record.term - record.number

    # Cálculo del porcentaje de deuda
    @api.depends('amount', 'current_debt')
    def _compute_percentage_debt(self):
        for record in self:
            if record.amount:
                record.percentage_debt = (record.current_debt / record.amount) * 100
            else:
                record.percentage_debt = 0

    # Cálculo de la tasa de interés efectiva
    @api.depends('interest_rate')
    def _compute_effective_interest_rate(self):
        for record in self:
            if record.interest_rate:
                record.effective_interest_rate = (((1 + record.interest_rate / 100) ** (1 / 12)) - 1)*100
            else:
                record.effective_interest_rate = 0

    # Cálculo de la deuda actual
    @api.depends('detail_ids.status', 'detail_ids.capital_remaining')
    def _compute_current_debt(self):
        for loan in self:
            # Filtrar cuotas pagadas y ordenarlas por fecha en orden descendente
            paid_details = loan.detail_ids.filtered(lambda d: d.status == 'paid').sorted(key=lambda d: d.date, reverse=True)
            # Obtener el capital_remaining de la última cuota pagada
            loan.current_debt = paid_details[0].capital_remaining if paid_details else 0
            loan.number = paid_details[0].number if paid_details else 0

    # Cálculo de los detalles del préstamo
    def compute_details(self):
        for loan in self:
            # Eliminar detalles existentes
            loan.detail_ids.unlink()

            # Datos del préstamo
            P = loan.amount  # Capital total
            r = (loan.effective_interest_rate) / 100  # Usar la tasa de interés efectiva mensual
            n = loan.term  # Duración en meses

            # Cuota fija (EMI) bajo el sistema francés
            if r > 0:
                emi = P * r * (1 + r) ** n / ((1 + r) ** n - 1)
            else:
                emi = P / n  # Sin interés, división simple

            # Inicialización de variables
            capital_remaining = P
            capital_amortized = 0
            # Configurar la fecha inicial de `detail_date`
            if loan.other_day_payment:
                # Primer pago el mismo día del siguiente mes
                detail_date = loan.date + relativedelta(months=1)
            else:
                # Primer pago el día 01 del siguiente mes
                detail_date = loan.date + relativedelta(months=1, day=1)

            # Generación de cuotas
            for i in range(1, n + 1):
                interest_amount = capital_remaining * r  # Intereses del mes
                capital_amount = emi - interest_amount  # Capital pagado en esta cuota
                capital_remaining -= capital_amount  # Capital restante
                capital_amortized += capital_amount  # Capital amortizado acumulado

                # Crear registro de detalle de cuota
                self.env['loan.details'].create({
                    'loan_id': loan.id,
                    'date': detail_date,
                    'total_payment': emi,
                    'interest_payment': interest_amount,
                    'capital_payment': capital_amount,
                    'capital_remaining': capital_remaining,
                    'capital_amortized': capital_amortized,
                    'number': i,
                })

                # Incrementar la fecha para los pagos subsecuentes
                detail_date += relativedelta(months=1)
