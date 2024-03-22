{
    'name': 'Jasman: Payment Reference',
    'summary': 'Personalized Payment Reference Logic and extra Fleet Vehicle field',
    'description':
    '''
        This module enhances the 'account.move' model by introducing new logic for 
        generating payment references. It employs various string combinations based 
        on different scenarios and appends a hash-like number as a suffix for bank verification. 
        Additionally, a new fields were added to both 'fleet.vehicle' and 'account.move'.

        - Developer: JCSG
        - Task ID: 3776817
    ''',
    'category': 'Custom Development',
    'version': '1.0.0',
    'author': 'Odoo Inc',
    'website': 'https://www.odoo.com',
    'license': 'OPL-1',
    'depends': [
        'fleet',
        'jasman_dimensiones',
    ],
    'data': [
        'views/account_move.xml',
        'views/fleet_vehicle.xml',
        'views/res_partner.xml',
    ],
}
