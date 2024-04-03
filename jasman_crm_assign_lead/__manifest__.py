{
    "name": "Jasman: Auto Assign Leads",
    "summary": "Auto assign leads based on location",
    "description": """
        Task ID: 3772324.
        Auto assign leads based on the client's location.
    """,
    "version": "1.0.0",
    "category": "Custom Developments",
    "license": "OPL-1",
    "author": "Odoo Development Services",
    "maintainer": "Odoo Development Services",
    "website": "www.odoo.com",
    "depends": ["base", "base_geolocalize", "crm"],
    "data": [
        "views/crm_team_views.xml",
    ],
}
