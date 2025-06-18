{
    "name": "Custom Gonzalo Expenses",
    "version": "18.0.1.0.0",
    "category": "Customizations",
    "author": "Gonzalo",
    "summary": "Custom reports for the client",
    "license": "AGPL-3",
    "application": True,
    "installable": True,
    "depends": [
        "base",
        "mail",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/expenses.xml",
        "views/expenses_menu.xml",
        "views/expenses_tags.xml",
        "views/expenses_payment_mode.xml",
        "views/expenses_type.xml",
        "views/expenses_secundary_tags.xml",
        "views/expenses_summary.xml",
    ],
}
