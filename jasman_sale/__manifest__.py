{
    "name": "Jasman Sale",
    "summary": """Jasman: Sale Order Adaptation""",
    "description": """
        - Add a field connecting fleet vehicle to a sale order and additional vehicle information
        - Add a boolean to sale orders for sales that require a vehicle
        - If this boolean is activated, sales can only be confirmed if the vehicle fields are filled in
        - Add the same boolean to the sales team, if a sale is created by a team with this field activated it should be true by default
        - Add a boolean to products that can only be sold in vehicle required sales, domain should reflect this field in sale order
        - Add fiscal position and account journal fields to the sales team, these should be set in sale orders created by that team
        - Add hr.department many2many in sales team to allow for multiple departments to be assigned to a team
        - Add hr.employee technician field in sale order line, only those in the same department as the sales team can be selected
        - Sales including lines with service products can only be confirmed if a technician is assigned to that line
        - Sale reports should show the assigned technician for later compensation
        - Include vehicle_id and vehicle_odometer in the invoice model and reports
        - Sale Orders should include a tab to attach photos of a vehicle (if the vehicle required bool is set)
        - These orders should not be able to be confirmed unless all photos are attached
        - Add a button in sale order to create a sign template copied from the template in the settings and link it to that order
        - Add binary fields for documents in the sale order and a computed field that combines all of them (pdf or png) to a single pdf
        - Add action to download combined pdf either from a single order or as a zip file if selecting multiple

        Developer: IASE
        Ticket ID: 3791307
    """,
    "author": "Odoo PS",
    "website": "https://www.odoo.com",
    "category": "Custom Development",
    "version": "1.0.0",
    "author": "Odoo Development Services",
    "maintainer": "Odoo Development Services",
    "website": "https://www.odoo.com/",
    "license": "OPL-1",
    "depends": [
        "account",
        "sale_management",
        "fleet",
        "crm",
        "sign",
        "hr"
    ],
    "demo": [
        "demo/ir_default_demo.xml",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/sign_data.xml",
        "data/ir_filters_data.xml",
        "views/account_move_views.xml",
        "views/crm_team_views.xml",
        "views/fleet_vehicle_views.xml",
        "views/product_template_views.xml",
        "views/report_saleorder.xml",
        "views/res_config_settings_views.xml",
        "views/res_partner_views.xml",
        "views/sale_order_views.xml",
        "views/sale_report_views.xml"
    ],
}
