# -*- coding: utf-8 -*-
{
    'name': "Mostrar opciones del menú de inventario.",

    'summary': """
        Permite la visualización de algunas opciones del menú y sub-menú, en el módulo de inventario.""",

    'description': """
        El módulo agrega una opción de menú llamada 
        1) Informes Oxford.
      
        El módulo crea 4 grupos de usuarios, que permite cada uno respectivamente:
        1) Visualizar el menú "Operaciones".
        2) Visualizar el menú "Informes".       
        3) Visualizar el sub menú "Desechar" del menú "Operaciones".
        4) Visualizar el sub menú "Informe de inventario" del menú "Informes".
    """,

    'author': "Techne Studio IT & Consulting",
    
    'website': "https://technestudioit.com/",
  
    'category': 'Inventory/Mostrar opciones del menú y submenú.',

    'version': '1.0',

    'license': "Other proprietary",

    'depends': ['base', 'stock'],

    "installable": True,
    
    "data": [     
            'security/show_inventory_menu.xml',
            ],
}
