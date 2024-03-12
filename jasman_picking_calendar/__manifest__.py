{
    'name': 'Pickings Calendar Color from Fleet',
    'description': '''
        Changes deliveries calendar color by partner to vehicle
        and assings vehicles to both stock picking and batches.

        Task ID: 3776808
    ''',
    'author': 'Odoo Development Services',
    'maintainer': 'Odoo Development Services',
    'website': 'https://www.odoo.com',
    'category': 'Custom Developments',
    'version': '1.0.0',
    'data': [
        'views/stock_picking_batch_views.xml',
        'views/stock_picking_views.xml',
    ],
    'depends': [
        'fleet',
        'stock_picking_batch',
        ],
    'license': 'OPL-1',
}
