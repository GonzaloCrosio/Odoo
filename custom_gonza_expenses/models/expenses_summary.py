import calendar
from datetime import date

from babel.dates import get_month_names

from odoo import api, fields, models


class ExpensesSummary(models.Model):
    _name = "exp.expenses.summary"
    _description = "Expenses Summary by Tags and Month"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name = "month"

    # Creo campo currency_id para almacenar la moneda del gasto-ingreso
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        required=True,
        default=lambda self: self.env.company.currency_id,
    )
    # Campos clave
    month = fields.Char(
        string="Month",
        required=True,
    )
    year = fields.Integer(
        string="Year",
        required=True,
    )
    # expenses_tag_id = fields.Many2one(
    #     comodel_name="exp.tag.expenses",
    #     string="Principal Tag",
    #     required=True,
    # )
    # expenses_secundary_tag_id = fields.Many2many(
    #     comodel_name="exp.tag.secundary.expenses",
    #     string="Secundary Tags",
    # )
    total_expenses = fields.Float(
        string="Total Expenses",
        required=True,
        default=0.0,
    )
    total_income = fields.Float(
        string="Total Income",
        required=True,
        default=0.0,
    )
    balance = fields.Float(
        string="Balance (Income - Expenses)",
        compute="_compute_balance",
        store=True,
    )
    # 👉 One2many computado, sin inverse: sirve para visualizar únicamente
    expense_ids = fields.One2many(
        comodel_name="exp.expenses.expenses",
        compute="_compute_expense_ids",
        string="Expenses",
        readonly=True,
        copy=False,
    )

    @api.depends("total_expenses", "total_income")
    def _compute_balance(self):
        for record in self:
            record.balance = record.total_income - record.total_expenses

    def _month_label_to_int(self, label):
        """Convierte el nombre de mes (según el idioma del entorno) a número (1-12)."""
        if not label:
            return False
        lang = self.env.lang or "en_US"
        # nombres localizados (enero, febrero, …)
        names = get_month_names("wide", locale=lang)  # {1: 'enero', ...}
        inv_local = {v.capitalize(): k for k, v in names.items()}
        m = inv_local.get(label)
        if m:
            return m
        # fallback en inglés si el label está en otro idioma
        import calendar as cal

        inv_en = {cal.month_name[i]: i for i in range(1, 13)}
        return inv_en.get(label)

    @api.depends("month", "year", "currency_id")
    def _compute_expense_ids(self):
        Expense = self.env["exp.expenses.expenses"]
        for rec in self:
            rec.expense_ids = [(6, 0, [])]
            if not rec.month or not rec.year:
                continue
            m = rec._month_label_to_int(rec.month)
            if not m:
                continue
            start = date(rec.year, m, 1)
            end = date(rec.year, m, calendar.monthrange(rec.year, m)[1])
            domain = [
                ("date", ">=", start),
                ("date", "<=", end),
            ]
            if rec.currency_id:
                domain.append(("currency_id", "=", rec.currency_id.id))
            expenses = Expense.search(domain, order="date asc, id asc")
            rec.expense_ids = [(6, 0, expenses.ids)]
