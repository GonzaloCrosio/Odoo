# tests/common.py

from odoo.tests.common import TransactionCase, tagged
from datetime import date


@tagged('gonza', 'post_install', '-at_install')
class CommonTest(TransactionCase):
    def setUp(self):
        super().setUp()

        Currency = self.env['res.currency']
        TagMain = self.env['exp.tag.expenses']
        TagSec = self.env['exp.tag.secundary.expenses']
        PaymentMode = self.env['exp.expenses.payment.mode']
        ExpenseType = self.env['exp.expenses.type']

        self.currency = self.env.company.currency_id
        self.main_tag = TagMain.create({'custom_name': 'Main Tag'})
        self.sec_tag = TagSec.create({'custom_name': 'Secondary Tag'})
        self.payment_mode = PaymentMode.create({'custom_name': 'Cash'})
        self.expense_type = ExpenseType.create({'custom_name': 'Business Expense'})

        # Relacionar secundaria compatible
        self.main_tag.compatible_secundary_tags_ids = [(6, 0, [self.sec_tag.id])]

        # Registro de gasto
        self.expense = self.env['exp.expenses.expenses'].create({
            'currency_id': self.currency.id,
            'expense_amount': 100.0,
            'income_amount': 50.0,
            'date': date(2025, 9, 1),
            'expenses_tag_id': self.main_tag.id,
            'expenses_secundary_tag_id': [(6, 0, [self.sec_tag.id])],
            'expenses_payment_mode_id': self.payment_mode.id,
            'expenses_type_id': self.expense_type.id,
        })
