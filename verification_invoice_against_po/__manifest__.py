# -*- coding: utf-8 -*-
{
    'name': "Verificación de factura contra orden de compra",

    'summary': """
        Verifica y actualiza automáticamente la cantidad de mercancía facturada con respecto a la recibida según la orden de compra""",

    'description': """
        Verifica y actualiza automáticamente la cantidad de mercancía facturada con respecto a la recibida según la orden de compra
    """,

    'author': "Techne Studio IT & Consulting",
    'website': "https://technestudioit.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Contabilidad',
    'version': '15.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock', 'sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
