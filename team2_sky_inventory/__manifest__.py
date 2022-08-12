# -*- coding: utf-8 -*-
{
    'name': "sky_inventory",

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
    'depends': ['base','stock','hr','etsi_hrms', 'sale_timesheet', 'hr_holidays'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/hr_dash_hide_view.xml',
        'views/hr_working_time.xml',
        'views/hr_manual_attendance.xml',
        'views/hr_settings.xml',
        'views/hr_emp_categ_id_context.xml',
        'views/hr_hide_asset.xml',
        'views/hr_hide_smart_button.xml',
        'views/hr_hide_states.xml',
        'views/hr_hide_bank_account_id.xml',
       
    ],
}