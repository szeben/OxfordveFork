# -*- coding: utf-8 -*-

from odoo import models, fields

class JournalType(models.Model):
    _inherit = 'account.journal' 

    is_custodian_type = fields.Boolean(
        string="¿Es de tipo custodio?",
        default = False
    )

    is_investment_type = fields.Boolean(
        string="¿Es de tipo inversión?",
        default = False
    )

    is_sale_point_type = fields.Boolean(
        string="¿Es de tipo punto de venta?",
        default = False
    )
       
    
   


    

