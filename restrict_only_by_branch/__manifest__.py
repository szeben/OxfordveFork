# -*- coding: utf-8 -*-
{
    'name': "Restricciones por rama activa o permitida",

    'summary': """
        Restringe el la visualización de información de acuerdo a la rama activa o la rama permitida de un usuario.""",

    'description': """
        Restringe el la visualización de información (contactos, pagos, facturas, pedidos de ventas, pedidos de compra y diarios) de acuerdo a la rama activa o la rama permitida de un usuario.
    """,

    'author': "Techne Studio IT & Consulting",
    'website': "https://technestudioit.com/",


    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting/Restricciones para extractos bancarios y conciliacion ',
    'version': '1.0',

    'license': 'Other proprietary',

    # any module necessary for this one to work correctly
    'depends': ['base', 'branch'],

    # always loaded
    'data': [
        'security/restricciones_por_rama.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
