{
    "name": "Jasman: Multiple Sale Order Templates",
    "summary": "Multiple Sale Order Templates per Order",
    "description": """
        Task ID: 3776834.
        Add new "Templates" tab to the sale order form view. This tab will contain a list of
        templates that can be applied to the sale order. When one of these templates is applied
        to the sale order, the products, quantities, sections and notes in the template will be
        added to the sale order.
    """,
    "version": "1.0.0",
    "category": "Custom Developments",
    "license": "OPL-1",
    "author": "Odoo Development Services",
    "maintainer": "Odoo Development Services",
    "website": "www.odoo.com",
    "depends": ["sale", "sale_management"],
    "data": [
        "views/sale_order_views.xml",
    ],
}
