# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError

class tsc_AccountPayment(models.Model):

    _inherit = 'account.payment'

    tsc_journal_ids = fields.Many2many('account.journal', string='Branch-filtered Journals', 
                                       store=False, readonly=False,
                                       compute='tsc_compute_tsc_journal_ids')

    def tsc_return_filtered_journal(self):
        return self.env['account.journal'].search([('type', 'in', ('bank', 'cash')),
                 ('company_id', '=', self.company_id.id),
                 '|',
                 ('branch_id','=',False),
                 ('branch_id','=',self.env.user.branch_id.id)
                 ])
    

    def tsc_compute_tsc_journal_ids(self):
        self.tsc_journal_ids = self.tsc_return_filtered_journal()

class tsc_AccountPaymentRegister(models.TransientModel):

    _inherit = 'account.payment.register'

    tsc_journal_ids = fields.Many2many('account.journal', string='Branch-filtered Journals', 
                                       store=False, readonly=False,
                                       compute='tsc_compute_tsc_journal_ids')
    

    def tsc_compute_tsc_journal_ids(self):
        self.tsc_journal_ids = self.env['account.journal'].search([('type', 'in', ('bank', 'cash')),
                 ('company_id', '=', self.company_id.id),
                 '|',
                 ('branch_id','=',False),
                 ('branch_id','=',self.env.user.branch_id.id)
                 ])

    




