# -*- coding: utf-8 -*-
{
    'name': "Control de Devoluciones",

    'summary': """
        Comprueba que las notas de crédito de facturas coincidan con devoluciones de inventario asociadas. 
    """,

    'description': """
        Permite asociar una devolución de inventario con una nota de crédito
        y al guardar la nota de crédito verifica automáticamente que dicha nota
        de crédito tenga los productos y las cantidades correctas, con respecto a la devolución.
    """,

    'author': "Techne Studio IT & Consulting",
    'website': "https://technestudioit.com/",

    'category': 'Accounting',
    'version': '0.1',

    'license': 'Other proprietary',

    # any module necessary for this one to work correctly
    'depends': ['base',
                'stock',
               'account'],

    # always loaded
    'data': [
        'security/acceso_devoluciones.xml',
        'wizard/account_move_reversal_view_inherit.xml',
        'views/stock_pick_inherit_views.xml',
        'views/account_move_inherit_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
