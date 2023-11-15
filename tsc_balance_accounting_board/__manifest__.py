# -*- coding: utf-8 -*-
{
    'name': "Balance on Accounting Board",

    'summary': """
       Displays on the dashboard an additional balance in a secondary currency based on the last recorded exchange rate. 
    """,

    'description': """
        Identifies which accounting journals will show an additional balance in secondary currency and displays it on the accounting dashboard, based on the last exchange rate recorded.
    """,

    'author': "Techne Studio IT & Consulting",
    'website': "https://technestudioit.com/",

    'category': 'Accounting',
    'version': '2.1',

    'license': 'Other proprietary',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'branch', 'branch_defaults'],

    # always loaded
    'data': [
        'views/tsc_account_journal_views.xml',
        'views/tsc_account_payment_views.xml',
        'views/tsc_account_move_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
