# -*- coding: utf-8 -*-
{
    'name': "Restringir los tipos de operaciones de entrada y salida",

    'summary': """
        Restricciones de Operaciones de tipo Envio y Entrada. """,

    'description': """
        Restringe la posibilidad de crear operaciones de inventario de tipo entrada y salida.
    """,

    'author': "Techne Studio IT & Consulting",
    'website': "https://technestudioit.com/",


    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Inventory/Restringir los tipos de operaciones entrada y salida.',
    'version': '1.0',

    'license': 'Other proprietary',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock', 'account', 'branch'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'security/restrict_the_operation_type_of_out_and_in.xml',
        # 'views/views.xml',
        # 'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
