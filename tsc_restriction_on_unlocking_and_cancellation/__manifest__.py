# -*- coding: utf-8 -*-
{
    'name': "Restrictions on unlocking or cancelling sale orders, purchase orders and invoices",

    'summary': """
       Allows authorized users to unlock confirmed sales and purchase orders, return published customer and vendor invoices to draft, cancel sales orders, and cancel customer invoices.
    """,

    'description': """
        Allows authorized users to unlock confirmed sales and purchase orders, return published customer and supplier invoices to draft, cancel sales orders, and cancel customer invoices that do not have confirmed shipments. All permissions are through user groups.
    """,

    'author': "Techne Studio IT & Consulting",
    'website': "https://technestudioit.com/",

    'version': '1.0',

    'license': 'Other proprietary',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        "security/tsc_access.xml",
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}