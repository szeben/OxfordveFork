# -*- coding: utf-8 -*-
{
    'name': "Marca de productos recibidos",

    'shortdesc': """
        Marca de productos recibidos
    """,

    'summary': """
        Incluye una marca en las órdenes de compra para identificar si fueron recibidos los productos.
    """,

    'description': """
        Incluye una marca en las órdenes de compra para identificar si fueron recibidos los productos.
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
    'depends': ['base', 'stock', 'purchase'],

    'installable': True,
    'auto_install': False,

    # always loaded
    'data': [
        'views/tsc_mark_products_received_views.xml',
    ],
    
}
