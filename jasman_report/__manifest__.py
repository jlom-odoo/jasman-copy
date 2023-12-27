{
    'name': '[B2] Changes to product.template',
    'summary': 'Automatize the products nomenclature.',
    'description': '''
        Allows to make reports of the sales of products by the product category, 
        parent of the product category and parent of the parent of the product 
        category (2 levels above in total).

        Task ID: 3593940
    ''',
    'author': 'Odoo Inc',
    'website': 'https://www.odoo.com',
    'category': 'Custom Developments',
    'version': '1.0.0',
    'data': [
        'report/sale_report_views.xml',
        'report/account_invoice_report_view.xml',
        'views/product_template_views.xml',
    ],
    'depends': ['account','sale'],
    'license': 'OPL-1',
}
