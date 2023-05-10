# -*- coding: utf-8 -*-
{
    'name': "Secuencias para OS y Guías de albaranes",

    'summary': """
        Modifica la secuencia de las OS y guías para incorporar consecutivos de acuerdo a la sucursal. 
    """,

    'description': """
        Modifica la secuencia de las Ordenes de venta, 
        Agrupaciones de Albaranes y Paquetes para incorporar
        prefijos y consecutivos de acuerdo a la rama en la que se generen.
    """,

    'author': "Techne Studio IT & Consulting",
    'website': "https://technestudioit.com/",

    'category': 'Inventory',
    'version': '0.1',

    'license': 'Other proprietary',

    # any module necessary for this one to work correctly
    'depends': ['base', 'branch', 'stock', 'stock_picking_batch', 'sale'],

    # always loaded
    'data': [
        'views/branch_extension.xml',
        'views/batch_extension.xml',
        'views/package_extension.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
