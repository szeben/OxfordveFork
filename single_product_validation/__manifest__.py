# -*- coding: utf-8 -*-
{
    'name': "Validación de producto único",

    'summary': """
        Valida que en un presupuesto u orden de venta no existan productos repetidos.""",

    'description': """
        Establece una validación en los presupuestos y ordenes de venta, que muestra un mensaje si existe algún producto repetido entre las líneas de pedido.
    """,

    'author': "Techne Studio IT & Consulting",
    'website': "https://technestudioit.com/",


    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sales/Validación de producto único',
    'version': '1.0',

    'license': 'Other proprietary',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale_management', 'branch'],

    # always loaded
    'data': [
        #'security/crear_e_importar_extractos_bancarios.xml',
        #'views/account_bank_statement_restrictions.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
