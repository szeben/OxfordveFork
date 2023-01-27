# -*- coding: utf-8 -*-
{
    'name': "Comisiones",

    'summary': """
        Modulo para el manejo de comisiones de acuerdo a la cantidad vendida de productos y por la cobranza realizada""",

    'description': """
        Permite configurar comisiones por producto y emitir un reporte por un periodo de tiempo para determinar la asignación de comisiones a los vendedores.
    """,

    'author': "Techne Studio IT & Consulting",
    'website': "https://technestudioit.com/",


    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sales/Comisiones',
    'version': '1.0',

    'license': 'Other proprietary',


    # any module necessary for this one to work correctly
    'depends': ['base', 'sale_management', 'stock', 'account', 'branch'],

    'installable': True,
    'application': True,
    'auto_install': False,

    # always loaded
    'data': [
        'security/commission_security.xml',
        'security/ir.model.access.csv',
        'views/commission_for_sale_views.xml',
        'views/commission_menuitem.xml',

    ],


}
