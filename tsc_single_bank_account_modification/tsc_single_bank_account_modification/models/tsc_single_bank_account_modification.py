# -*- coding: utf-8 -*-

from odoo import _, api, exceptions, fields, models
from odoo.exceptions import ValidationError, RedirectWarning

class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'    

    _sql_constraints = [
        ('unique_number', 'check(1=1)', 'Account Number must be unique'),
    ]   
    
    @api.onchange('acc_number')
    def onchange_acc_number(self):
        res = {}
        rpb = self.env['res.partner.bank'].search([('acc_number','=', self.acc_number)])

        if rpb:
            res['warning'] = { 
                'title': _('Important!'), 
                'message': _('The account number that you will proceed to save already exists in the system.')}
            return res       

