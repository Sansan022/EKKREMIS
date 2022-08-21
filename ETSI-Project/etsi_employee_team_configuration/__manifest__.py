# -*- coding: utf-8 -*-
{
    'name': "etsi_employee_teams_configuration",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['base', 'hr', 'etsi_hrms',],

    'data': [
        'views/config.xml',
        'views/sequence.xml',
    ],
}