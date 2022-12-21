# -*- coding: utf-8 -*-
{
    'name': "Restringir el tipo de operación de salida",

    'summary': """
        Restricciones de Operaciones de tipo Envio""",

    'description': """
        Restringe la posibilidad de crear operaciones de inventario de tipo envio, con excepcion de un grupo de usuario especial.
    """,

    'author': "Techne Studio IT & Consulting",
    'website': "https://technestudioit.com/",


    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Inventory/Restringir el tipo de operación de salida ',
    'version': '1.0',

    'license': 'Other proprietary',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock', 'account', 'branch'],

    # always loaded
    'data': [        
        'security/restringir_operaciones_envio.xml',       
    ], 
}
