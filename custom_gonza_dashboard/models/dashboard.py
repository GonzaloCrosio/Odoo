from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class DashboardControl(models.Model):
    _name = "dashboard.control"
    _description = "Dashboard Model"
    _inherit = ["mail.thread", "mail.activity.mixin"]
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
        string="Interest Rate (%)", required=True, help="Nominal annual interest rate."
    )
    term = fields.Integer(
        string="Term in months",
        required=True,
    )
    detail_ids = fields.One2many(
        comodel_name="loan.details", inverse_name="loan_id", string="Details"
    )
    effective_interest_rate = fields.Float(
        string="Effective Interest Rate Monthly",
        compute="_compute_effective_interest_rate",
        store=True,
        help="Effective monthly interest rate calculated from the nominal annual rate.",
    )
    other_day_payment = fields.Boolean(
        string="Signing day first pay day",
    )
    current_debt = fields.Float(
        string="Current Debt",
        compute="_compute_current_debt",
        store=True,
        help="Capital remaining from the last paid installment.",
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
    total_interest = fields.Float(
        string="Total Interest",
        readonly=True,
        help="Total interest paid over the life of the loan.",
    )
    total_amount_to_pay = fields.Float(
        string="Total Amount to Pay",
        readonly=True,
        help="Total amount to be repaid (principal + interest).",
    )
    is_investment = fields.Boolean(
        string="Is Investment",
        help="Indicates if the loan is used for investment purposes.",
    )
    simulated_npv = fields.Float(
        string="Simulated Investment NPV",
        compute="compute_simulated_npv",
        store=True,
        help="Net present value of an investment that uses the loan, considering an expected return.",
    )
    expected_return_rate = fields.Float(
        string="Expected Investment Return (%)",
        default=8.0,
        help="Expected annual rate of return on the investment.",
    )
    simulated_vfn = fields.Float(
        string="Simulated Investment VFN",
        compute="compute_simulated_vfn",
        store=True,
        digits=(16, 2),
        help="Net future value of an investment that uses the loan, considering an expected return.",
    )
    is_finished = fields.Boolean(
        string="Is Finished",
        help="Indicates if the loan has been fully repaid.",
        default=False,
        store=True,
    )

    # Cálculo del número de pagos pendientes
    @api.depends("number", "term")
    def _compute_number_payments(self):
        for record in self:
            record.number_payments = record.term - record.number

    # Cálculo del porcentaje de deuda
    @api.depends("amount", "current_debt")
    def _compute_percentage_debt(self):
        for record in self:
            if record.amount:
                record.percentage_debt = (record.current_debt / record.amount) * 100
            else:
                record.percentage_debt = 0

    # Cálculo de la tasa de interés efectiva
    @api.depends("interest_rate")
    def _compute_effective_interest_rate(self):
        for record in self:
            if record.interest_rate:
                record.effective_interest_rate = (
                    ((1 + record.interest_rate / 100) ** (1 / 12)) - 1
                ) * 100
            else:
                record.effective_interest_rate = 0

    # Cálculo de la deuda actual
    @api.depends("detail_ids.status", "detail_ids.capital_remaining")
    def _compute_current_debt(self):
        for loan in self:
            # Filtrar cuotas pagadas y ordenarlas por fecha en orden descendente
            paid_details = loan.detail_ids.filtered(
                lambda d: d.status == "paid"
            ).sorted(key=lambda d: d.date, reverse=True)
            # Obtener el capital_remaining de la última cuota pagada
            loan.current_debt = paid_details[0].capital_remaining if paid_details else 0
            loan.number = paid_details[0].number if paid_details else 0

    # Validación de campos requeridos antes del cálculo
    def _validate_required_fields(self):
        for loan in self:
            missing_fields = []
            if not loan.amount:
                missing_fields.append("Amount")
            if not loan.term:
                missing_fields.append("Term")
            if not loan.interest_rate:
                missing_fields.append("Interest Rate")
            if not loan.date:
                missing_fields.append("Date")

            if missing_fields:
                raise ValidationError(
                    _(
                        "The payment plan cannot be calculated because the following fields are missing: %s"
                    )
                    % ", ".join(missing_fields)
                )

    # Cálculo de los detalles del préstamo
    def compute_details(self):
        # Validación limpia y reutilizable para campos requeridos
        self._validate_required_fields()

        for loan in self:
            # Eliminar detalles existentes
            loan.detail_ids.unlink()

            # Datos del préstamo
            P = loan.amount  # Capital total
            r = (
                loan.effective_interest_rate
            ) / 100  # Usar la tasa de interés efectiva mensual
            n = loan.term  # Duración en meses

            # Cuota fija (EMI) bajo el sistema francés
            if r > 0:
                emi = P * r * (1 + r) ** n / ((1 + r) ** n - 1)
            else:
                emi = P / n  # Sin interés, división simple

            # Inicialización de variables
            capital_remaining = P
            capital_amortized = 0
            total_interest = 0
            total_amount = 0

            # Configurar la fecha inicial de `detail_date`
            if loan.other_day_payment:
                # Primer pago el mismo día de firma
                detail_date = loan.date
            else:
                # Primer pago el día 01 del siguiente mes
                detail_date = loan.date + relativedelta(months=1, day=1)

            # Generación de cuotas
            for i in range(1, n + 1):
                # Determinar si es la primera cuota y se paga el mismo día (no interés)
                if i == 1 and loan.other_day_payment:
                    interest_amount = 0.0
                    capital_amount = emi
                else:
                    # Si se paga normal calculamos interés
                    interest_amount = capital_remaining * r
                    capital_amount = emi - interest_amount

                # Actualizar capital
                capital_remaining -= capital_amount
                capital_amortized += capital_amount

                # Acumulados
                total_interest += interest_amount
                total_amount += emi

                # Crear registro de detalle de cuota
                self.env["loan.details"].create(
                    {
                        "loan_id": loan.id,
                        "date": detail_date,
                        "total_payment": emi,
                        "interest_payment": interest_amount,
                        "capital_payment": capital_amount,
                        "capital_remaining": capital_remaining,
                        "capital_amortized": capital_amortized,
                        "number": i,
                    }
                )

                # Incrementar la fecha para los pagos subsecuentes
                detail_date += relativedelta(months=1)

                # Asignar los valores calculados al préstamo de total intereses y total a pagar
                loan.total_interest = total_interest
                loan.total_amount_to_pay = total_amount

    # Cálculo del VAN simulado para inversiones --- npv = net present value
    # No se puede hacer un api.depends porque necesita que existan las cuotas
    def compute_simulated_npv(self):
        for loan in self:
            # loan.compute_details() Lo comento porque no quiero que me genere las cuotas
            # Si se actualiza la TAE no se actualiza el resultado del VAN
            expected_monthly_rate = (1 + loan.expected_return_rate / 100) ** (
                1 / 12
            ) - 1
            if not loan.detail_ids:
                loan.simulated_npv = 0
                loan.simulated_vfn = 0
                continue

            # Ordenar cuotas por fecha
            sorted_details = loan.detail_ids.sorted(key=lambda d: d.date)

            try:
                # NPV = Ingreso inicial - valor presente de pagos
                pv_of_payments = sum(
                    [
                        detail.total_payment / ((1 + expected_monthly_rate) ** i)
                        for i, detail in enumerate(sorted_details, start=1)
                    ]
                )

                npv = loan.amount - pv_of_payments  # Ingreso - egresos descontados

                loan.simulated_npv = round(npv, 2)

                # Llamada al metodo VFN
                loan.compute_simulated_vfn()
            except Exception:
                loan.simulated_npv = 0
                loan.simulated_vfn = 0

    def compute_simulated_vfn(self):
        """
        Calcula el Valor Futuro Neto (VFN) de un préstamo/inversión,
        considerando que cada cuota se capitaliza hasta el final del préstamo
        usando la tasa esperada de retorno.
        """
        for loan in self:
            if not loan.detail_ids:
                loan.simulated_vfn = 0
                continue

            # Convertimos la tasa anual esperada a mensual
            expected_monthly_rate = (1 + loan.expected_return_rate / 100) ** (
                1 / 12
            ) - 1

            # Ordenamos cuotas por fecha
            sorted_details = loan.detail_ids.sorted(key=lambda d: d.date)

            try:
                n = len(sorted_details)
                # VF = suma de cada cuota capitalizada hasta el último mes
                fv_of_payments = sum(
                    [
                        detail.total_payment * ((1 + expected_monthly_rate) ** (n - i))
                        for i, detail in enumerate(sorted_details, start=1)
                    ]
                )

                # VF de la inversión inicial (al final del préstamo)
                fv_of_initial_amount = loan.amount * ((1 + expected_monthly_rate) ** n)

                vfn = fv_of_initial_amount - fv_of_payments
                loan.simulated_vfn = round(vfn, 2)
            except Exception:
                loan.simulated_vfn = 0
