# -*- coding: utf-8 -*-
{
    'name': "Bank statement print customization",

    'summary': """
        Change the format of the bank statement document""",

    'description': """
        Change the format of the bank statement document
    """,

    'author': "Techne Studio IT & Consulting",
    'website': "https://technestudioit.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Contabilidad',
    'version': '15.0.0.1',
    'license': 'Other proprietary',


    # any module necessary for this one to work correctly
    'depends': ['base', 'account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'report/tsc_papper_format.xml',
        'report/tsc_ir_actions_report.xml',
        'report/tsc_report_statement.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
