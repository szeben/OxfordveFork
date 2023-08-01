# -*- coding: utf-8 -*-
{
    'name': "Restrict reprocessing of validated extract",

    'summary': """
        Restricts unauthorized users from returning to the "processing" state of 
        validated extracts""",

    'description': """
        Restricts unauthorized users from returning to the "processing" state of 
        validated extracts. In the list, the validated extracts are shown with green letters
    """,

    'author': 'Techne Studio IT & Consulting',
    'website': 'https://technestudioit.com/',
    'license': 'Other proprietary',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'security/reprocessing_validated_extract.xml',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
