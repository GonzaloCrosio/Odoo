from odoo import fields, models, api


class LoanDetails(models.Model):
    _name = 'loan.details'
    _description = 'Loan Details'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "loan_id"

    # Creo campo currency_id para almacenar la moneda del préstamo
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        required=True,
        default=lambda self: self.env.company.currency_id
    )
    loan_id = fields.Many2one(
        comodel_name='loan.loan',
        string="Loan",
        required=True,
        ondelete='cascade'
    )
    date = fields.Date(
        string="Payment Date",
        required=True
    )
    total_payment = fields.Float(
        string="Total Payment",
        required=True
    )
    interest_payment = fields.Float(
        string="Interest Payment",
        required=True
    )
    capital_payment = fields.Float(
        string="Capital Payment",
        required=True
    )
    capital_remaining = fields.Float(
        string="Capital Remaining",
        required=True
    )
    capital_amortized = fields.Float(
        string="Capital Amortized",
        required=True
    )
    status = fields.Selection(
        selection=[
            ('paid', "Paid"),
            ('pending', "Pending"),
        ],
        string="Status",
        required=True,
        default='pending',
    )
    number = fields.Integer(
        string="Number",
        required=True,
        help="Sequential number"
    )
