# -*- coding: utf-8 -*-

from odoo import models, api, fields

class RamaExtendida(models.Model):
    
    #_inherit = 'res.branch'
    _inherit = 'res.company'
    _description = 'Extensión a la Rama'
    
    puerto_libre = fields.Boolean(string='Puerto Libre')
    