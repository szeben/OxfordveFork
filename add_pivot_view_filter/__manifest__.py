# -*- coding: utf-8 -*-
{
    'name': "Filtros en vista pivote de Análisis de factura",

    'summary': """
        Filtro por marca, código de barra, referencia interna y 
        fecha de pago de factura en vista pivote de 
        Análisis de factura""",

    'description': """
        Filtro por marca, código de barra, referencia interna y 
        fecha de pago de factura en vista pivote de 
        Análisis de factura
    """,

    'author': "Techne Studio IT & Consulting",
    'website': "https://technestudioit.com/",

    'license': "Other proprietary",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        # 'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
