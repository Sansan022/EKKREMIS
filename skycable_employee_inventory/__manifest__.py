# -*- coding: utf-8 -*-
{

    'name': "skycable_employee_inventory_system",

    'summary': """
        Created and modified by the Titans. Do not try to edit or you\'ll face the consequences and the wrath of titan. Goodluck to you!""",

    'description': """
        Long description of module's purpose
    """,

    'author': "WSI GANG",
    'website': "http://www.yourcompany.com",
    'category': 'Warehouse',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','stock','procurement','purchase','product','contacts', 'account', 'sale', 'project', 'website_partner','crm','etsi_base','etsi_hrms','etsi_payroll'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'data/skycable_inventory_adjustment_sequence.xml',
        'views/skycable_inventory_all_transfer_views.xml',
        'views/skycable_inventory_adjustment_views.xml',
        'views/skycable_inventory_operation_type_views.xml',
        'views/skycable_inventory_products_views.xml',
        'views/skycable_employee_configuration_sequence.xml',
        'views/skycable_employee_teams_configuration.xml',
        'views/skycable_contact_configuration.xml',
        # Phase 3
        'views/skycable_operation_return.xml',
        'views/team_issuance_views.xml',
        


        'views/skycable_employee_hr_dash_hide_view.xml',
        'views/skycable_employee_hr_hide_asset.xml',
        'views/skycable_employee_hr_hide_states.xml',
        'views/skycable_employee_hr_hide_smart_button.xml',
        'views/skycable_employee_default_category.xml',
        'views/skycable_employee_hr_hide_bank_account_id.xml',
        'views/skycable_employee_hr_working_time.xml',
        'views/skycable_employee_hr_settings.xml',
        'views/skycable_employee_hr_manual_attendance.xml',
        'views/skycable_product_product.xml',
        'views/skycable_inventory_all_transfer_return.xml',

    ]
}