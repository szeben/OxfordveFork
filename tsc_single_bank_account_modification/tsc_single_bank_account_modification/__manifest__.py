# -*- coding: utf-8 -*-
{
    'name': "Single Bank Account Validation Modification",

    'shortdesc': """
        Single Bank Account Validation Modification
    """,

    'summary': """
        Allows the registration of repeated account numbers, displaying a confirmation message.
    """,

    'description': """
        Allows the registration of repeated account numbers, displaying a confirmation message.
    """,
   
    'author': "Techne Studio IT & Consulting",
    'website': "https://technestudioit.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Inventory',
    'version': '15.0.0.1',
    'license': 'Other proprietary',

    # any module necessary for this one to work correctly
    'depends': ['base', 'contacts'],

    'installable': True,
    'auto_install': False,

    # always loaded
    'data': [
       
    ],
    
}
