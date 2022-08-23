# -*- coding: utf-8 -*-
{

    'name': "skycable_employee_inventory_system",

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
    'depends': ['base','stock','procurement','purchase','product', 'etsi_hrms'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/skycable_inventory_all_transfer_views.xml',
        'views/skycable_inventory_adjustment_views.xml',
        'views/skycable_inventory_operation_type_views.xml',
        'views/skycable_inventory_products_views.xml',
        'views/skycable_employee_configuration_sequence.xml',
        'views/skycable_employee_configuration_sequence.xml'
    ]
}