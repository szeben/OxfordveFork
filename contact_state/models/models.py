# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ContactState(models.Model):
    _inherit = 'res.partner' 
    state = fields.Selection(
        [
            ('new', 'Nuevo'),
            ('validated', 'Validado')
        ],
        string='State',
        tracking=True,
        default='new'        
    )

    def action_validated(self):
        self.state = 'validated'
        self.active = True
    
    def action_new(self):
        self.state = 'new'
        self.active = False

    @api.model
    def create(self, vals):
        record = super(ContactState, self).create(vals)           
        record.active = False
        return record


    

