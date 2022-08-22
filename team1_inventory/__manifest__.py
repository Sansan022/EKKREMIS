# -*- coding: utf-8 -*-
{
    'name': "team1_inventory",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Team 1 - Odoo Training",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/10.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Warehouse',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','stock','procurement','purchase','product','stock_account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/inventory_views_inherit.xml',
        'views/templates.xml',
        'views/operation_type_views_inherit.xml',
        'views/quantiy_on_hand_btn_form.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}