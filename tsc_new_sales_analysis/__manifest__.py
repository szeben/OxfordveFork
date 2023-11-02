# -*- coding: utf-8 -*-
{
    'name': "New sales analysis",

    'summary': """
        Includes a new sales analysis pivot view without accessing detailed information. Only visible to authorized users.""",

    'description': """
        Includes a new sales analysis pivot view without accessing detailed information. Only visible to authorized users.
    """,

    'author': "Techne Studio IT & Consulting",
    'website': "https://technestudioit.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '15.0.1.0',
    'license': 'Other proprietary',
    'category': 'Ventas',

    # any module necessary for this one to work correctly
    'depends': ['base', 'branch'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'security/tsc_security.xml',
        'views/tsc_sale_menu.xml',
        'views/tsc_ir_menu.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
