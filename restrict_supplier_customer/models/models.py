# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ContactState(models.Model):
    _inherit = 'res.partner' 
    
    is_national =  fields.Boolean(string="National")