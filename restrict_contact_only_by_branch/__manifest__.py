# -*- coding: utf-8 -*-
{
    'name': "Acceder a contactos de acuerdo a las ramas permitidas",

    'summary': """
        Permite el acceso a los contactos de acuerdo a las ramas permitidas para el usuario""",

    'description': """
        Crea reglas para permitir el acceso a los contactos de acuerdo a las ramas permitidas.
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
        'security/acceder a contactos de acuerdo a las ramas permitidas.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
