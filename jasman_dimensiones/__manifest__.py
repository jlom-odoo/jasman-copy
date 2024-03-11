{
    "name": "Jasman Dimensiones",
    "summary": """Jasman: Extra Fields""",
    "description": """
        Jasman: add fields to crm.team, res.user and l10n_mx_edi.payment.method

        When an account.move.lien is created or updated, the analytic_distribution field is updated with the new fields.

        Developer: ELCE, GECM
        Ticket ID: 3587114, 3791172
    """,
    "author": "Odoo PS",
    "website": "https://www.odoo.com",
    "category": "Custom Development",
    "version": "1.0",
    "depends": ["account", "crm", "l10n_mx_edi"],
    "data": [
        "views/crm_team.xml",
        "views/payment_method.xml",
        "views/res_user.xml",
    ],
    "license": "OPL-1",
}
