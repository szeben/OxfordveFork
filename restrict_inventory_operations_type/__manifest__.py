# -*- coding: utf-8 -*-
{
    'name': "Restringir tipos de operaciones de inventario",

    'summary': """
        Restringe la posibilidad de crear o validar operaciones de inventario.
    """,

    'description': """
        Restringe la posibilidad de crear o validar operaciones de inventario 
        (entradas, salidas, transferencias internas).
    """,

    'author': "Techne Studio IT & Consulting",
    'website': "https://technestudioit.com/",


    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Inventory',
    'version': '0.1',

    'license': 'Other proprietary',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock'],

    # always loaded
    'data': [
        'security/acceso_transferencias_internas.xml',
        'views/stock_picking_inherit_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
