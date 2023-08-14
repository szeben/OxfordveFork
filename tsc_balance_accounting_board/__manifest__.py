# -*- coding: utf-8 -*-
{
    'name': "Balance on Accounting Board",

    'summary': """
       Displays an additional balance in a secondary currency on the dashboard. 
    """,

    'description': """
        Identifies which accounting journals will show an additional balance in secondary currency, and displays the same on the accounting dashboard.
    """,

    'author': "Techne Studio IT & Consulting",
    'website': "https://technestudioit.com/",

    'category': 'Accounting',
    'version': '0.1',

    'license': 'Other proprietary',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account'],

    # always loaded
    'data': [
        'views/tsc_account_journal_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
