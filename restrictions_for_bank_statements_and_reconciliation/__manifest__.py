# -*- coding: utf-8 -*-
{
    'name': "Restricciones para extractos bancarios y conciliacion",

    'summary': """
        Restringe el proceso de gestion de extractos bancarios y conciliacion de pagos""",

    'description': """
        Crea grupos de usuarios especiales para la gestion de extractos bancarios (guardar, publicar y validar) y la conciliacion de pagos.
    """,

    'author': "Techne Studio IT & Consulting",
    'website': "https://technestudioit.com/",


    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting/Restricciones para extractos bancarios y conciliacion ',
    'version': '1.0',

    'license': 'Other propietary',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock', 'account', 'branch'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'security/crear_e_importar_extractos_bancarios.xml',
        # 'views/views.xml',
        # 'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
