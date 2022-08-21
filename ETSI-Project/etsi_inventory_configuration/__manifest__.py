# -*- coding: utf-8 -*-
{

    'name': "etsi_inventory_configuration",

    'summary': """
        Created and modified by the Titans. Do not try to edit or you\'ll face the consequences and the wrath of titan. Goodluck to you!""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Team 1 - Odoo Training",
    'website': "http://www.yourcompany.com",
    'category': 'Warehouse',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','stock','procurement','purchase','product', 'etsi_employee_team_configuration'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/etsi_all_transfer_views.xml',
        'views/etsi_inventory_adjustment_views.xml',
        'views/etsi_operation_type_views.xml',
        'views/etsi_products_views.xml',

    ]
}