{
    "name": "Jasman Extra Fields",
    "summary": """Jasman: Extra Fields""",
    "description": """
        Jasman: add fields to crm.team, res.user and account.payment.term

        Developers: ELCE, GECM
        Ticket ID: 3587114
    """,
    "author": "Odoo Inc",
    "maintainer": "Odoo Inc",
    "website": "https://www.odoo.com",
    "category": "Custom Development",
    "version": "1.0",
    "depends": ["crm", "account"],
    "data": [
        "views/crm_team.xml",
        "views/account_payment_term_views_inherit.xml",
        "views/res_user.xml",
    ],
    "license": "OPL-1",
}
