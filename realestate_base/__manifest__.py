{
    "name": "Real Estate - Base",
    "version": "19.0.1.0.0",
    "category": "Real Estate",
    "summary": "Shared models for the Real Estate suite: provinces, "
               "property types and the abstract base property.",
    "description": """
Base module of the Real Estate suite.

Provides shared building blocks used by the Sale, Rent and Zone Knowledge
modules:
  * realestate.province      - Argentine provinces (data included).
  * realestate.property.type - User-editable property types.
  * realestate.property      - Abstract model with the common fields
                               (owner, address, characteristics, currency).
It also creates the root "Real Estate" menu and the Configuration menus.
""",
    "author": "Custom Development",
    "website": "",
    "license": "LGPL-3",
    "depends": ["base"],
    "data": [
        "security/ir.model.access.csv",
        "data/realestate_province_data.xml",
        "data/realestate_property_type_data.xml",
        "views/realestate_province_views.xml",
        "views/realestate_property_type_views.xml",
        "views/realestate_menus.xml",
    ],
    "installable": True,
    "application": True,
}
