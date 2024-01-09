{
    "name": "Jasman: Partner Extra Fields",
    "summary": "This module adds extra fields to the partner model.",
    "description":
    """
        Adds the following fields to the partner model: [active, jasman_id,
        property_account_payable_group_id, channel_analytic_account_id, confirm_delivery,
        invoice_user_id, guarantee_expiry, contract_expiry, supplier_credit_limit,
        supplier_payment_way, supplier_invoice_user_id, pay_day, payment_reference]

        Adds two automated actions to set the payment reference according to the
        payment reference of the partner. And to set the invoice_date_due according to
        the payment day of the partner.

        - Developer: ARMM
        - Task ID: 3599933
    """,
    "category": "Custom Development",
    "version": "1.0.0",
    "author": "Odoo Development Services",
    "maintainer": "Odoo Development Services",
    "website": "https://www.odoo.com/",
    "license": "OPL-1",
    "depends": [
        "purchase",
        "account_followup",
        "web_studio",
    ],
    "data": [
        "data/ir_action_server.xml",
        "data/base_automation.xml",
        "views/account_followup_views.xml",
        "views/res_partner_bank_views.xml",
        "views/res_partner_views.xml",
    ],
}
