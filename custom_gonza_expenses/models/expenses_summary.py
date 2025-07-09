from odoo import models, fields, api


class ExpensesSummary(models.Model):
    _name = 'exp.expenses.summary'
    _description = 'Expenses Summary by Tags and Month'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "expenses_tag_id"

    # Creo campo currency_id para almacenar la moneda del gasto-ingreso
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        required=True,
        default=lambda self: self.env.company.currency_id
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
    expenses_tag_id = fields.Many2one(
        comodel_name="exp.tag.expenses",
        string="Principal Tag",
        required=True,
    )
    expenses_secundary_tag_id = fields.Many2many(
        comodel_name="exp.tag.secundary.expenses",
        string="Secundary Tags",
    )
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

    @api.depends('total_expenses', 'total_income')
    def _compute_balance(self):
        for record in self:
            record.balance = record.total_income - record.total_expenses

