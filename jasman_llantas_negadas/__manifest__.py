{
    "name": "Jasman: Llantas Negadas",
    "summary": "This module helps to store missing tires",
    "description":
    """
        This module will add a one2many field to the sale.order to keep track of all tires that were not available
        when making the sales order.
        - Developer: AALA
        - Task ID: 3791315
    """,
    "category": "Custom Development",
    "version": "1.0.0",
    "author": "Odoo Development Services",
    "maintainer": "Odoo Development Services",
    "website": "https://www.odoo.com/",
    "license": "OPL-1",
    "depends": ["sale_management"],
    "data": [
        "security/ir.model.access.csv",
        "views/missing_tire_views.xml",
        "views/sale_order_views.xml"
    ],
}
