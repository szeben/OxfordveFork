# -*- coding: utf-8 -*-
{
    'name': "Restricciones sobre Productos",

    'summary': """
        Restringe la visualización y gestión de productos en el módulo de Inventario.""",

    'description': """
        Restringe la visualización y gestión de productos que se pueden comprar, 
        vender o que son un gasto, desde el módulo de Inventario.
    """,

    'author': "Techne Studio IT & Consulting",
    'website': "https://technestudioit.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Inventario',
    'version': '0.1',
    'license': "Other proprietary",

    # any module necessary for this one to work correctly
    'depends': ['base', 'product', 'stock'],

    # always loaded
    'data': [
        'security/constraints_on_products_security.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
