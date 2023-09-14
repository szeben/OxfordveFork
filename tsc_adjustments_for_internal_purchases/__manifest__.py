# -*- coding: utf-8 -*-
{
    'name': "Adjustments for Internal Purchases",

    'summary': """
       Restricts the display of product categories and warehouses on products of internal use.
    """,

    'description': """
        Restricts the display of product categories and warehouses on products of internal use.
    """,

    'author': "Techne Studio IT & Consulting",
    'website': "https://technestudioit.com/",

    'category': 'Inventory',
    'version': '0.1',

    'license': 'Other proprietary',

    # any module necessary for this one to work correctly
    'depends': ['base', 'product', 'stock', 'purchase', 'purchase_stock'],

    # always loaded
    'data': [
        'security/tsc_access.xml',
        'views/tsc_product_category.xml',
        'views/tsc_stock_picking_type_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}