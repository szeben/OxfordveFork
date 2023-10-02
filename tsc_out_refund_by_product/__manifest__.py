# -*- coding: utf-8 -*-
{
    'name': "Rectifying Invoice per Product",

    'summary': """
        Includes a list view to consult rectifying invoices by product.
    """,

    'description': """
        Includes a list view to consult rectifying invoices by product.
    """,

    'author': "Techne Studio IT & Consulting",
    'website': "https://technestudioit.com/",
    
    'category': 'Accounting',
    'version': '0.1',
    'license': "Other proprietary",

    # any module necessary for this one to work correctly
    'depends': ['base', 'branch', 'account', 'sale', 'sale_management', 'account_accountant'],

    # always loaded
    'data': [
        'views/tsc_credit_note_per_product.xml',
        'security/tsc_credit_note_per_product.xml',
    ],
    # only loaded in demonstration mode
    'demo': [

    ],

}
