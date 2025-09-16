from datetime import date

from odoo.tests.common import TransactionCase, tagged


@tagged("gonza", "post_install", "-at_install")
class CommonTest(TransactionCase):
    def setUp(self):
        super().setUp()
        Loan = self.env["loan.loan"]
        self.loan = Loan.create(
            {
                "name": "Test Loan",
                "amount": 10000,
                "interest_rate": 12.0,
                "term": 12,
                "date": date(2025, 1, 1),
            }
        )
