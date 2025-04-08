{
    "name": "Custom Gonzalo Loans",
    "version": "17.0.1.0.0",
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
        "views/loan_loan.xml",
        "views/loan_menu.xml",
    ],
}
