{
    "name": "Real Estate - Zone Knowledge",
    "version": "19.0.1.0.0",
    "category": "Real Estate",
    "summary": "Prospecting intelligence about properties in the zone for "
               "future sale opportunities.",
    "description": """
Zone Knowledge.

Stores intelligence about specific properties that could become future sale
opportunities, and the information needed to keep a close, trusting
relationship with the owners / neighbors:
  * House data: rooms, bathrooms, square meters, owner / inhabitants,
    two free-text observation fields.
  * Contact and rapport information for future follow-up.
  * One2many lines to register the individual units / departments of a
    building or 'finca', each one a potential sale on its own.
""",
    "author": "Custom Development",
    "license": "LGPL-3",
    "depends": ["realestate_base", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "data/realestate_zone_sequence.xml",
        "views/realestate_zone_views.xml",
        "views/realestate_zone_menus.xml",
    ],
    "installable": True,
    "application": False,
}
