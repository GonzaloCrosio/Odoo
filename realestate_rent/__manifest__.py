{
    "name": "Real Estate - Rent",
    "version": "19.0.1.0.0",
    "category": "Real Estate",
    "summary": "Manage properties for rent (available, rented, inactive).",
    "description": """
Properties for Rent.

Mirrors the Sale module but for the rental business: commercial status
(Available, Rented, Inactive), owner, full address, characteristics and the
relevant rental figures (owner's expected rent, current rent value, market
rent and safe rent value), plus tenant and contract dates.
""",
    "author": "Custom Development",
    "license": "LGPL-3",
    "depends": ["realestate_base", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "data/realestate_rent_sequence.xml",
        "views/realestate_rent_property_views.xml",
        "views/realestate_rent_menus.xml",
    ],
    "installable": True,
    "application": False,
}
