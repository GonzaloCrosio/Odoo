from odoo import models, fields, api
from babel.dates import format_date


class Expenses(models.Model):
    _name = 'exp.expenses.expenses'
    _description = 'Expenses Model'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "expenses_tag_id"

    # Creo campo currency_id para almacenar la moneda del gasto-ingreso
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        required=True,
        default=lambda self: self.env.company.currency_id
    )
    expense_amount = fields.Float(
        string="Expense Amount",
        required=True,
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
        string="Expenses Type",
    )
    compatible_secundary_tags_ids = fields.Many2many(
        comodel_name="exp.tag.secundary.expenses",
        string="Compatible Secondary Tags (Related)",
        related="expenses_tag_id.compatible_secundary_tags_ids",
        readonly=True,
    )

    # Creo el onchange para que me filtre las tags secundarias segun la principal
    @api.onchange('expenses_tag_id')
    def _onchange_expenses_tag_id(self):
        if self.expenses_tag_id:
            self.expenses_secundary_tag_id = False
            return {
                'domain': {
                    'expenses_secundary_tag_id': [
                        ('id', 'in', self.expenses_tag_id.compatible_secundary_tags_ids.ids)]}}
        else:
            return {'domain': {'expenses_secundary_tag_id': []}}

    # Metodo para preparar los datos del resumen
    def _prepare_summary_values(self):
        summary_data = []
        lang = self.env.lang or "en_US"

        for record in self:
            month = format_date(record.date, format='MMMM', locale=lang).capitalize()
            year = record.date.year

            # Obtener lista de IDs de etiquetas secundarias
            secondary_tag_ids = record.expenses_secundary_tag_id.ids

            summary_data.append({
                'month': month,
                'year': year,
                'expenses_tag_id': record.expenses_tag_id.id,
                'expenses_secundary_tag_id': [(6, 0, secondary_tag_ids)],
                'total_expenses': record.expense_amount,
                'total_income': record.income_amount,
            })
        return summary_data

    # Sobrescribir el metodo create
    @api.model
    def create(self, vals):
        record = super(Expenses, self).create(vals)

        summary_values = record._prepare_summary_values()

        for values in summary_values:
            # Extraer IDs para búsqueda
            secondary_tag_ids = values['expenses_secundary_tag_id'][0][2] if values[
                'expenses_secundary_tag_id'] else []

            summary = self.env['exp.expenses.summary'].search([
                ('month', '=', values['month']),
                ('year', '=', values['year']),
                ('expenses_tag_id', '=', values['expenses_tag_id']),
            ], limit=1)

            # Si existe un gasto con la etiqueta lo suma
            if summary:
                summary.total_expenses += values['total_expenses']
                summary.total_income += values['total_income']
            # Si no existe un gasto con la etiqueta lo crea
            else:
                self.env['exp.expenses.summary'].create(values)

        return record

    # Sobrescribir el metodo write
    def write(self, vals):
        for record in self:
            # Guardar los valores originales antes de actualizarlos
            original_summary_values = record._prepare_summary_values()

            # Actualizar el registro actual
            super(Expenses, record).write(vals)

            # Restar los valores originales del resumen
            for values in original_summary_values:

                # Extraer IDs para búsqueda
                secondary_tag_ids = values['expenses_secundary_tag_id'][0][2] if values[
                    'expenses_secundary_tag_id'] else []

                summary = self.env['exp.expenses.summary'].search([
                    ('month', '=', values['month']),
                    ('year', '=', values['year']),
                    ('expenses_tag_id', '=', values['expenses_tag_id']),
                ], limit=1)
                if summary:
                    summary.total_expenses -= values['total_expenses']
                    summary.total_income -= values['total_income']
                    # Eliminar el registro si los totales son 0
                    if summary.total_expenses == 0.0 and summary.total_income == 0.0:
                        summary.unlink()

            # Agregar los nuevos valores al resumen
            new_summary_values = record._prepare_summary_values()
            for values in new_summary_values:
                # Extraer IDs para búsqueda
                secondary_tag_ids = values['expenses_secundary_tag_id'][0][2] if values[
                    'expenses_secundary_tag_id'] else []

                summary = self.env['exp.expenses.summary'].search([
                    ('month', '=', values['month']),
                    ('year', '=', values['year']),
                    ('expenses_tag_id', '=', values['expenses_tag_id']),
                ], limit=1)
                if summary:
                    summary.total_expenses += values['total_expenses']
                    summary.total_income += values['total_income']
                else:
                    self.env['exp.expenses.summary'].create(values)

        return True

    # Sobrescribir el metodo unlink
    def unlink(self):
        for record in self:
            # Preparar los valores para los totales a eliminar
            summary_values = record._prepare_summary_values()

            # Ajustar los totales en el resumen
            for values in summary_values:

                # Extraer IDs para búsqueda
                secondary_tag_ids = values['expenses_secundary_tag_id'][0][2] if values[
                    'expenses_secundary_tag_id'] else []

                summary = self.env['exp.expenses.summary'].search([
                    ('month', '=', values['month']),
                    ('year', '=', values['year']),
                    ('expenses_tag_id', '=', values['expenses_tag_id']),
                ], limit=1)
                if summary:
                    summary.total_expenses -= values['total_expenses']
                    summary.total_income -= values['total_income']
                    # Eliminar el resumen si los totales son 0
                    if summary.total_expenses == 0.0 and summary.total_income == 0.0:
                        summary.unlink()

        # Eliminar los registros actuales
        return super(Expenses, self).unlink()
