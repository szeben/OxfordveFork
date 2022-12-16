# -*- coding: utf-8 -*-
{
    'name': "Mostrar opciones del menú de contabilidad.",

    'summary': """
        Permite la visualización de algunas opciones del menú y sub-menú, en el módulo de contabilidad.""",

    'description': """
        Permite la visualización de algunas opciones del menú y submenú, en el módulo de contabilidad.       
        El módulo crea 7 grupos de usuarios, que permite cada uno respectivamente:
        1) Visualizar el menú "Clientes.
        2) Visualizar el menú "Proveedores".
        3) Visualizar el menú "Contabilidad".
        4) Visualizar el menú "Clientes->Pagos".
        5) Visualizar el sub menú "Pagos" del menú "Clientes".
        6) Visualizar el sub menú "Libro Mayor" del menú "Contabilidad" e "Informe".
        7) Visualizar el sub menú "Vencidos por cobrar" del menú "Informes".
    """,

    'author': "Techne Studio IT & Consulting",
    
    'website': "https://technestudioit.com/",
  
    'category': 'Accounting/Mostrar opciones del menú y submenú.',

    'version': '1.0',

    'license': "Other proprietary",

    'depends': ['base', 'sale', 'purchase', 'account'],

    "installable": True,
    
    "data": [
            'security/show_account_menu.xml',
            ],
}
