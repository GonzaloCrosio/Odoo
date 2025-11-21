from .common import CommonTest
# AssertAlmostEqual es mejor para comparar floats porque permite definir la precisión
# y evita errores por pequeñas diferencias en la representación interna de los números.
# AssertEqual busca igualdad exacta.
# AsstertTrue verifica que una condición sea verdadera.

class TestLoan(CommonTest):
    # Verifica que la TAE mensual se calcule correctamente a partir de la TNA anual
    def test_compute_effective_interest_rate(self):
        self.loan._compute_effective_interest_rate()
        # Fórmula: ((1 + rate) ** (1/12)) - 1
        expected = ((1 + 0.12) ** (1 / 12) - 1) * 100
        self.assertAlmostEqual(self.loan.effective_interest_rate, expected, places=5)

    # Verifica que se generen correctamente las líneas de detalle del préstamo
    def test_compute_details(self):
        self.loan.compute_details()
        self.assertEqual(len(self.loan.detail_ids), self.loan.term)
        total_capital = sum(self.loan.detail_ids.mapped("capital_payment"))
        total_interest = sum(self.loan.detail_ids.mapped("interest_payment"))
        total_payment = sum(self.loan.detail_ids.mapped("total_payment"))

        self.assertAlmostEqual(total_capital, self.loan.amount, places=2)
        self.assertAlmostEqual(self.loan.total_interest, total_interest, places=2)
        self.assertAlmostEqual(self.loan.total_amount_to_pay, total_payment, places=2)

    # Verifica que la deuda actual y el número de la última cuota pagada se calculen correctamente
    def test_compute_current_debt(self):
        self.loan.compute_details()
        # Simula pago de 3 cuotas
        paid_lines = self.loan.detail_ids[:3]
        paid_lines.write({"status": "paid"})

        self.loan._compute_current_debt()
        # Debe coincidir con el capital_remaining de la última cuota pagada
        self.assertEqual(self.loan.current_debt, paid_lines[-1].capital_remaining)
        self.assertEqual(self.loan.number, paid_lines[-1].number)

    # Verifica que el porcentaje de deuda se calcule correctamente
    def test_compute_percentage_debt(self):
        self.loan.compute_details()
        # Marca la cuota 1 como pagada
        first_line = self.loan.detail_ids[0]
        first_line.write({"status": "paid"})
        self.loan._compute_current_debt()
        self.loan._compute_percentage_debt()

        expected = (self.loan.current_debt / self.loan.amount) * 100
        self.assertAlmostEqual(self.loan.percentage_debt, expected, places=2)

    # Verifica que el número de pagos restantes se calcule correctamente
    def test_compute_number_payments(self):
        self.loan.number = 5
        self.loan.term = 12
        self.loan._compute_number_payments()
        self.assertEqual(self.loan.number_payments, 7)

    # Verifica que el NPV simulado se calcule correctamente
    def test_compute_simulated_npv(self):
        self.loan.compute_details()
        self.loan.compute_simulated_npv()

        # El NPV debe ser un número real (no None)
        self.assertTrue(self.loan.simulated_npv is not None)

    # Verifica que el VFN simulado se calcule correctamente
    def test_compute_simulated_vfn(self):
        self.loan.compute_details()
        self.loan.compute_simulated_vfn()
        self.assertTrue(self.loan.simulated_vfn is not None)
