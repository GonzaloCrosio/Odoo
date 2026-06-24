{
    "name": "Real Estate - Sale",
    "version": "19.0.1.0.0",
    "category": "Real Estate",
    "summary": "Manage properties for sale (portfolio, sold, inactive).",
    "description": """
Properties for Sale.

Registers the properties handled by the agency with their commercial status
(In Portfolio, Sold, Inactive), the owner, the full address, the physical
characteristics and the relevant valuation figures (owner's expected value,
current sale value, market price and safe sale value).
""",
    "author": "Custom Development",
    "license": "LGPL-3",
    "depends": ["realestate_base", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "data/realestate_sale_sequence.xml",
        "views/realestate_sale_property_views.xml",
        "views/realestate_sale_menus.xml",
    ],
    "installable": True,
    "application": False,
}
