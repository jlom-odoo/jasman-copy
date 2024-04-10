{
    "name": "Jasman: Custom Delivery Guide",
    "description":
    """
        Makes it possible to generate a Delivery Guide
        (Carta Porte) in a batch delivery order, instead
        of a single delivery order.

        - Developer: JLOM
        - Task ID: 3776824
    """,
    "category": "Custom Development",
    "version": "1.0.0",
    "author": "Odoo Development Services",
    "maintainer": "Odoo Development Services",
    "website": "https://www.odoo.com/",
    "license": "OPL-1",
    "depends": [
        "stock_picking_batch",
        "l10n_mx_edi_stock_extended_30",
    ],
    "data": [
        "data/cfdi_cartaporte_30.xml",
        "views/stock_picking_views.xml",
        "views/stock_picking_batch_views.xml",
    ],
}
