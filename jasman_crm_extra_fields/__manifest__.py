{
    "name": "Jasman Extra Fields",
    "summary": """Jasman: Extra Fields""",
    "description": """
        Jasman: add fields to crm.team, res.user and l10n_mx_edi.payment.method

        Developer: ELCE
        Ticket ID: 3587114
    """,
    "author": "Odoo PS",
    "website": "https://www.odoo.com",
    "category": "Custom Development",
    "version": "1.0",
    "depends": ["crm", "l10n_mx_edi"],
    "data": [
        "views/crm_team.xml",
        "views/payment_method.xml",
        "views/res_user.xml",
    ],
    "license": "OPL-1",
    "installable": True,
    "application": True,
}
