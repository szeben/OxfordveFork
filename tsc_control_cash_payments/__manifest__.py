# -*- coding: utf-8 -*-
{
    'name': "Control of cash payments",

    'summary': "Allows the registration of cash payments only for certain users. Automatically generate statements for cash payments to suppliers",

    'description': "Allows the registration of cash payments only for certain users. Creating a new usergroup for this. Automatically generate statements for cash payments to suppliers.",

    'author': "Techne Studio IT & Consulting",
    'website': "https://technestudioit.com/",

    'license': "Other proprietary",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['account_accountant'],

    # always loaded
    'data': [
        'views/views.xml',
    ],
}
