# -*- coding: utf-8 -*-
{
    'name': "team2_sky_inventory",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/10.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
<<<<<<< HEAD:team1_inventory/__manifest__.py
    'depends': ['base','stock','procurement','purchase','product'],
=======
    'depends': ['base','stock','hr','etsi_hrms', 'sale_timesheet', 'hr_holidays'],
>>>>>>> 31235fa86106c67a5653f66d376a1998cf995b1c:team2_sky_inventory/__manifest__.py

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
<<<<<<< HEAD:team1_inventory/__manifest__.py
        'views/inventory_views_inherit.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
=======
        'views/hr_dash_hide_view.xml',
        'views/hr_working_time.xml',
        'views/hr_manual_attendance.xml',
        'views/hr_settings.xml',
        'views/hr_emp_categ_id_context.xml',
        'views/hr_hide_asset.xml',
        'views/hr_hide_smart_button.xml',
        'views/hr_hide_states.xml',
        'views/hr_hide_bank_account_id.xml',
       
>>>>>>> 31235fa86106c67a5653f66d376a1998cf995b1c:team2_sky_inventory/__manifest__.py
    ],
}