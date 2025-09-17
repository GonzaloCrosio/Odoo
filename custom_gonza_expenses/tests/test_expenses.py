# tests/test_exp_expenses.py

from .common import CommonTest


class TestExpenses(CommonTest):

    # Verificar que el resumen se crea correctamente al crear un gasto, que devuelva un
    # solo resultado, el mes, año y los importes sean correctos
    def test_prepare_summary_values(self):
        values = self.expense._prepare_summary_values()
        self.assertEqual(len(values), 1)
        self.assertEqual(values[0]['month'], 'September')
        self.assertEqual(values[0]['year'], 2025)
        self.assertEqual(values[0]['total_expenses'], 100.0)
        self.assertEqual(values[0]['total_income'], 50.0)

    # Verifica que solo exista 1 resumen
    # Verifica las sumas en ese resumen
    # Verifica el create
    def test_create_summary_update(self):
        # Creamos un segundo gasto en el mismo mes
        second_expense = self.env['exp.expenses.expenses'].create({
            'currency_id': self.currency.id,
            'expense_amount': 200.0,
            'income_amount': 100.0,
            'date': self.expense.date,
            'expenses_tag_id': self.main_tag.id,
            'expenses_secundary_tag_id': [(6, 0, [self.sec_tag.id])],
            'expenses_payment_mode_id': self.payment_mode.id,
            'expenses_type_id': self.expense_type.id,
        })

        summary = self.env['exp.expenses.summary'].search([
            ('month', '=', 'September'),
            ('year', '=', 2025)
        ])
        self.assertEqual(len(summary), 1)
        self.assertEqual(summary.total_expenses, 300.0)
        self.assertEqual(summary.total_income, 150.0)

    # Verifica el write y las sumas en el resumen
    def test_write_summary_update(self):
        # Modificar los montos del gasto
        self.expense.write({'expense_amount': 300.0, 'income_amount': 100.0})

        summary = self.env['exp.expenses.summary'].search([
            ('month', '=', 'September'),
            ('year', '=', 2025)
        ])
        self.assertEqual(summary.total_expenses, 300.0)
        self.assertEqual(summary.total_income, 100.0)

    # Verifica el unlink y que el resumen se elimine si no hay más gastos en ese mes/año
    def test_unlink_summary_cleanup(self):
        self.expense.unlink()

        summary = self.env['exp.expenses.summary'].search([
            ('month', '=', 'Septiembre'),
            ('year', '=', 2025)
        ])
        self.assertEqual(len(summary), 0)

    # Verifica que el dominio de las etiquetas secundarias se actualice correctamente
    def test_onchange_expenses_tag_id(self):
        result = self.expense._onchange_expenses_tag_id()
        domain_ids = result.get('domain', {}).get('expenses_secundary_tag_id', [])[0][2]

        self.assertTrue(self.sec_tag.id in domain_ids)
