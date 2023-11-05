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
    'version': '2.0',

    'license': 'Other proprietary',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'branch'],

    # always loaded
    'data': [
        'views/tsc_account_journal_views.xml',
        'views/tsc_actions_overrides.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
