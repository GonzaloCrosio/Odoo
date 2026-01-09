{
    "name": "Custom Gonzalo Dashboard",
    "version": "19.0.1.0.0",
    "category": "Customizations",
    "author": "Gonzalo Crosio",
    "summary": "Custom Personal Project Gonzalo Dashboard",
    "license": "AGPL-3",
    "application": True,
    "installable": True,
    "depends": [
        "mail",
        "web",
    ],
    "assets": {
        "web.assets_backend": [
            "custom_gonza_dashboard/static/src/css/financial_dashboard.css",
        ],
    },
    "data": [
        "security/ir.model.access.csv",
        "views/financial_indicators_views.xml",
        "views/dashboard_control.xml",
        "views/dashboard_menu.xml",
    ],
}
