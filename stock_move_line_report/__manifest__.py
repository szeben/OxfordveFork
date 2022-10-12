# -*- coding: utf-8 -*-
{
    'name': 'Informe de movimiento de productos',

    'summary': """
            Informe de movimiento de productos.
        """,

    'description': """
        Nuevas columnas en el informe Movimientos de productos, en el módulo de Inventario: Código, número, cliente/proveedor, entrada, salida y saldo en existencia.
    """,

    'author': "Techne Studio IT & Consulting",
    'website': "https://technestudioit.com/",

    'license': "Other proprietary",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/stock_move_line_tree.xml',
    ],
    # only loaded in demonstration mode
    # 'demo': [
    #    'demo/demo.xml',
    # ],
}
