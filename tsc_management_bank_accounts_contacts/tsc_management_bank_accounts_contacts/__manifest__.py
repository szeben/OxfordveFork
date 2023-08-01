# -*- coding: utf-8 -*-
{
    'name': "Management of Bank Accounts for Contacts",

    'summary': """
       Restricts bank accounts registration that are associated with a contact. Displays the contact's account in certain payment operations where said information was not visible before.
    """,

    'description': """
        Restricts bank accounts registration that are associated with a contact. Displays the contact's account in certain payment operations where said information was not visible before.
    """,

    'author': "Techne Studio IT & Consulting",
    'website': "https://technestudioit.com/",

    'category': 'Accounting',
    'version': '0.1',

    'license': 'Other proprietary',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail', 'account'],

    # always loaded
    'data': [
        'security/tsc_access.xml',
        'security/ir.model.access.csv',
        'views/tsc_bank_views.xml',
        'views/tsc_payment_views.xml',
        'wizard/tsc_payment_wizard.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}