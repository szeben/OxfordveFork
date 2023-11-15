# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError

class tsc_AccountMove(models.Model):

    _inherit = 'account.move'

    tsc_journal_ids = fields.Many2many('account.journal', string='Branch-filtered Journals', 
                                       store=False, readonly=False,
                                       compute='tsc_compute_tsc_journal_ids')
    
    def tsc_compute_tsc_journal_ids(self):
        self.tsc_journal_ids = self.env['account.journal'].search([
                 '|',
                 ('branch_id','=',False),
                 ('branch_id','=',self.env.user.branch_id.id)
                 ])    

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        domain = domain or []
        tsc_default_move_type = self.env.context.get('default_move_type')
        if tsc_default_move_type in ['out_invoice', 'out_refund', 'in_invoice', 'in_refund', 'entry']:
            domain.extend(['|', ('branch_id','=',False),
                       ('branch_id','=',self.env.user.branch_id.id)])
        return super(tsc_AccountMove, self).search_read(domain, fields, offset, limit, order)


class tsc_AccountMoveLine(models.Model):

    _inherit = 'account.move.line'

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        domain = domain or []        
        tsc_journal_type = self.env.context.get('journal_type')
        tsc_search_default_posted = self.env.context.get('search_default_posted') 
        if tsc_journal_type in ['sales', 'general', 'purchase', 'bank'] and tsc_search_default_posted == 1:
            domain.extend(['|', ('branch_id','=',False),
                       ('branch_id','=',self.env.user.branch_id.id)])
        return super(tsc_AccountMoveLine, self).search_read(domain, fields, offset, limit, order)