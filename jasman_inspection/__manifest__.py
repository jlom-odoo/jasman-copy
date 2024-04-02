{
    'name': 'Sale and Task Inspections',
    'description': '''
        Adds task templates for service products and inspection
        lines to these tasks. Allows to add optional products
        from priority inspection lines to sale order. Allows to
        create crm opportunity and linked sale order with optional
        products that weren't sold.

        Task ID: 3757512
    ''',
    'author': 'Odoo Development Services',
    'maintainer': 'Odoo Development Services',
    'website': 'https://www.odoo.com',
    'category': 'Custom Developments',
    'version': '1.0.0',
    'data': [
        'security/ir.model.access.csv',
        'views/crm_stage_views.xml',
        'views/inspection_line_views.xml',
        'views/project_task_views.xml',
        'views/sale_order_views.xml',
        'views/product_template_views.xml',
    ],
    'depends': ['sale_project', 'crm'],
    'license': 'OPL-1',
}
