from babel.dates import format_date
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class Expenses(models.Model):
    _name = "exp.expenses.expenses"
    _description = "Expenses Model"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name = "expenses_tag_id"

    # Creo campo currency_id para almacenar la moneda del gasto-ingreso
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        required=True,
        default=lambda self: self.env.company.currency_id,
    )
    expense_amount = fields.Float(
        string="Expense Amount",
        required=True,
        aggregator="sum", # Para que aparezca en la PIVOT y sume en la Kanban
    )
    income_amount = fields.Float(
        string="Income Amount",
        required=True,
    )
    description = fields.Text(
        string="Description",
    )
    date = fields.Date(
        string="Date",
        required=True,
    )
    expenses_tag_id = fields.Many2one(
        comodel_name="exp.tag.expenses",
        string="Principal Tags",
    )
    # Creo el domain para que solo me aparezcan las compatibles con la tag principal
    expenses_secundary_tag_id = fields.Many2many(
        comodel_name="exp.tag.secundary.expenses",
        string="Secundary Tags",
        domain="[('id', 'in', compatible_secundary_tags_ids)]",
    )
    expenses_payment_mode_id = fields.Many2one(
        comodel_name="exp.expenses.payment.mode",
        string="Payment Mode",
    )
    expenses_type_id = fields.Many2one(
        comodel_name="exp.expenses.type",
        string="Related Operation",
    )
    compatible_secundary_tags_ids = fields.Many2many(
        comodel_name="exp.tag.secundary.expenses",
        string="Compatible Secondary Tags (Related)",
        related="expenses_tag_id.compatible_secundary_tags_ids",
        readonly=True,
    )
    pdf_attachment = fields.Binary(
        string="PDF Attachment Document",
        attachment=True,
        help="Attach a PDF file related to this expense or income.",
    )
    # Gastos Recurrentes
    is_recurring = fields.Boolean(
        string="Repetitive",
        default=False,
        tracking=True,
    )
    recurrence_frequency = fields.Selection(
        selection=[("monthly", "Monthly"),
                   ("yearly", "Yearly")],
        string="Frequency",
        default="monthly",
        tracking=True,
    )
    recurrence_interval = fields.Integer(
        string="Every",
        default=1,
        help="Repeat every N months/years.",
        tracking=True,
    )
    recurrence_end_date = fields.Date(
        string="Repeat Until",
        tracking=True,
    )
    recurrence_parent_id = fields.Many2one(
        "exp.expenses.expenses",
        string="Recurrence Parent",
        index=True,
        ondelete="cascade",
    )
    recurrence_child_ids = fields.One2many(
        "exp.expenses.expenses",
        "recurrence_parent_id",
        string="Recurring Expenses",
    )

    # Creo el onchange para que me filtre las tags secundarias segun la principal
    @api.onchange("expenses_tag_id")
    def _onchange_expenses_tag_id(self):
        if self.expenses_tag_id:
            self.expenses_secundary_tag_id = False
            return {
                "domain": {
                    "expenses_secundary_tag_id": [
                        (
                            "id",
                            "in",
                            self.expenses_tag_id.compatible_secundary_tags_ids.ids,
                        )
                    ]
                }
            }
        else:
            return {"domain": {"expenses_secundary_tag_id": []}}

    # Metodo para preparar los datos del resumen
    def _prepare_summary_values(self):
        summary_data = []
        # Obtener el idioma del usuario actual y sino del sistema (por defecto es en_US)
        lang = self.env.lang or "en_US"

        for record in self:
            month = format_date(record.date, format="MMMM", locale=lang).capitalize()
            year = record.date.year

            summary_data.append(
                {
                    "month": month,
                    "year": year,
                    "total_expenses": record.expense_amount,
                    "total_income": record.income_amount,
                }
            )
        return summary_data

    # Heredar el metodo create
    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)

        for record in records:
            summary_values = record._prepare_summary_values()
            for values in summary_values:
                summary = self.env["exp.expenses.summary"].search(
                    [
                        ("month", "=", values["month"]),
                        ("year", "=", values["year"]),
                    ],
                    limit=1,
                )

                if summary:
                    summary.total_expenses += values["total_expenses"]
                    summary.total_income += values["total_income"]
                else:
                    self.env["exp.expenses.summary"].create(values)

        # Generación de gastos recurrentes (solo para padres)
        if not self.env.context.get("skip_recurrence_generation"):
            parents = records.filtered(lambda x: x.is_recurring and not x.recurrence_parent_id)
            if parents:
                parents._sync_recurrence_children()

        return records

    # Heredar el metodo write
    def write(self, vals):
        for record in self:
            # Guardar los valores originales antes de actualizarlos
            original_summary_values = record._prepare_summary_values()

            # Actualizar el registro actual
            super(Expenses, record).write(vals)

            # Restar los valores originales del resumen
            for values in original_summary_values:
                summary = self.env["exp.expenses.summary"].search(
                    [
                        ("month", "=", values["month"]),
                        ("year", "=", values["year"]),
                    ],
                    limit=1,
                )
                if summary:
                    summary.total_expenses -= values["total_expenses"]
                    summary.total_income -= values["total_income"]
                    # Eliminar el registro si los totales son 0
                    if summary.total_expenses == 0.0 and summary.total_income == 0.0:
                        summary.unlink()

            # Agregar los nuevos valores al resumen
            new_summary_values = record._prepare_summary_values()
            for values in new_summary_values:
                summary = self.env["exp.expenses.summary"].search(
                    [
                        ("month", "=", values["month"]),
                        ("year", "=", values["year"]),
                    ],
                    limit=1,
                )
                if summary:
                    summary.total_expenses += values["total_expenses"]
                    summary.total_income += values["total_income"]
                else:
                    self.env["exp.expenses.summary"].create(values)

        # Para Gastos Repetitivos - Paso variable por contexto
        if not self.env.context.get("skip_recurrence_generation"):
            trigger_fields = {"is_recurring", "date", "recurrence_end_date", "recurrence_frequency", "recurrence_interval"}
            if trigger_fields.intersection(vals.keys()):
                parents = self.filtered(lambda r: not r.recurrence_parent_id)
                parents._sync_recurrence_children()

        return True

    # Heredar el metodo unlink
    def unlink(self):
        for record in self:
            # Preparar los valores para los totales a eliminar
            summary_values = record._prepare_summary_values()

            # Ajustar los totales en el resumen
            for values in summary_values:
                summary = self.env["exp.expenses.summary"].search(
                    [
                        ("month", "=", values["month"]),
                        ("year", "=", values["year"]),
                    ],
                    limit=1,
                )
                if summary:
                    summary.total_expenses -= values["total_expenses"]
                    summary.total_income -= values["total_income"]
                    # Eliminar el resumen si los totales son 0
                    if summary.total_expenses == 0.0 and summary.total_income == 0.0:
                        summary.unlink()

        # Eliminar los registros actuales
        return super().unlink()

    # Gastos Recurrentes
    # Evitar crear gastos recurrentes contradictorios
    @api.constrains("is_recurring", "date", "recurrence_end_date", "recurrence_interval")
    def _check_recurrence_dates(self):
        for expenses in self:
            if not expenses.is_recurring:
                continue
            if not expenses.recurrence_end_date:
                raise ValidationError(_("Repeat Until is required for recurring expenses."))
            if expenses.recurrence_end_date < expenses.date:
                raise ValidationError(_("Repeat Until must be >= Date."))
            if expenses.recurrence_interval < 1:
                raise ValidationError(_("Every must be >= 1."))

    # Le da inicio y fin a la repetición del gasto
    def _iter_recurrence_dates(self):
        self.ensure_one()
        if not self.is_recurring or not self.recurrence_end_date:
            return
        # Determina la frecuencia de repetición
        step = (
            relativedelta(months=self.recurrence_interval)
            if self.recurrence_frequency == "monthly"
            else relativedelta(years=self.recurrence_interval)
        )
        # Repite el gasto hasta la fecha de fin
        next_date = self.date + step
        while next_date <= self.recurrence_end_date:
            yield next_date
            next_date = next_date + step

    # Crea los gastos hijos y elimina los fuera de fecha
    def _sync_recurrence_children(self):
        for expenses in self:
            if not expenses.is_recurring:
                # Si se desmarca, podemos decidir si borrar hijos o no. Decido no eliminarlos
                # expenses.recurrence_child_ids.unlink()
                continue

            desired_dates = set(expenses._iter_recurrence_dates()) # Rango de Fecha de Repetición
            existing_children = expenses.recurrence_child_ids
            existing_by_date = {c.date: c for c in existing_children}

            # 1) Borrar hijos fuera del rango (por ejemplo si acortas la fecha fin)
            to_delete = existing_children.filtered(lambda c: c.date not in desired_dates)
            if to_delete:
                to_delete.unlink()

            # 2) Crear los que falten
            missing_dates = [d for d in sorted(desired_dates) if d not in existing_by_date]
            if not missing_dates:
                continue

            # Copiamos datos del padre, pero desactivamos recurrencia en los hijos
            # para que no generen más.
            base_vals = expenses.copy_data()[0]
            base_vals.update({
                "is_recurring": False,
                "recurrence_frequency": False,
                "recurrence_interval": 1,
                "recurrence_end_date": False,
                "recurrence_parent_id": expenses.id,
            })

            vals_list = []
            for d in missing_dates:
                vals = dict(base_vals)
                vals["date"] = d
                vals_list.append(vals)

            # Contexto para evitar recursión en create()
            self.with_context(skip_recurrence_generation=True).create(vals_list)
