# -*- coding: utf-8 -*-
{
    'name': "Mostrar opciones del menú de contabilidad.",

    'summary': """
        Permite la visualización de algunas opciones del menú y sub-menú, en el módulo de contabilidad.""",

    'description': """
        El módulo agrega dos opciones de menú:
        1) Contabilidad Oxford.
        2) Informes Oxford.
      
        El módulo crea 8 grupos de usuarios, que permite cada uno respectivamente:
        1) Visualizar el menú "Clientes.
        2) Visualizar el menú "Proveedores".
        3) Visualizar el menú "Contabilidad".
        4) visualizar el menú "Informes ".       
        5) Visualizar el sub menú "Pagos" del menú "Clientes".
        6) Visualizar el sub menú "Libro Mayor" del menú "Contabilidad" e "Informe".
        7) Visualizar el sub menú "Vencidos por cobrar" del menú "Informes".
        8) Visualizar el sub menú "Vencidos por pagar" del menú "Informes".       
    """,

    'author': "Techne Studio IT & Consulting",
    
    'website': "https://technestudioit.com/",
  
    'category': 'Accounting/Mostrar opciones del menú y submenú.',

    'version': '1.0',

    'license': "Other proprietary",

    'depends': ['base', 'sale', 'purchase', 'account', 	'account_accountant'],

    "installable": True,
    
    "data": [     
            'security/show_account_menu.xml',
            'security/ir.model.access.csv',
            ],
}
