{
    'name': 'Jasman: Pricing with access rights',
    'description': '''
        Conduct sales order checks to ensure the sales team is making profitable deals.
        Restrictions based on user configurations and permissions.
        
        Developer: [cmgv]
        Task ID: 3755390
    ''',
    'author': 'Odoo Development Services',
    'maintainer': 'Odoo Development Services',
    'website': 'https://www.odoo.com',
    'category': 'Custom Developments',
    'version': '1.0.0',
    'data': [
        'views/account_move_views.xml',
        'views/product_pricelist_item_views.xml',
        'views/product_views.xml',
        'views/res_users_views.xml',
        'views/sale_order_views.xml',
        ],
    'demo':[
        'demo/ir_default_demo.xml'
    ],
    'depends': ['account','sale_management','sale_margin','purchase'],
    'license': 'OPL-1',
}
