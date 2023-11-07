# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError

class tsc_AccountJournal(models.TransientModel):

    _inherit = 'account.payment.register'

    """
    @api.model
    def _get_batch_journal(self, batch_result):
        payment_values = batch_result['payment_values']
        foreign_currency_id = payment_values['currency_id']
        partner_bank_id = payment_values['partner_bank_id']

        currency_domain = [('currency_id', '=', foreign_currency_id)]
        partner_bank_domain = [('bank_account_id', '=', partner_bank_id)]

        default_domain = [
            ('type', 'in', ('bank', 'cash')),
            ('company_id', '=', batch_result['lines'].company_id.id),
            '|', 
           ('branch_id','=',False),
           ('branch_id','=',self.env.user.branch_id.id)
        ]

        if partner_bank_id:
            extra_domains = (
                currency_domain + partner_bank_domain,
                partner_bank_domain,
                currency_domain,
                [],
            )
        else:
            extra_domains = (
                currency_domain,
                [],
            )

        for extra_domain in extra_domains:
            journal = self.env['account.journal'].search(default_domain + extra_domain, limit=1)
            if journal:
                return journal

        return self.env['account.journal']

    @api.depends('can_edit_wizard', 'company_id')
    def _compute_journal_id(self):
        for wizard in self:
            if wizard.can_edit_wizard:
                batch = wizard._get_batches()[0]
                wizard.journal_id = wizard._get_batch_journal(batch)
            else:
                wizard.journal_id = self.env['account.journal'].search([
                    ('type', 'in', ('bank', 'cash')),
                    ('company_id', '=', wizard.company_id.id),
                    '|', 
                   ('branch_id','=',False),
                   ('branch_id','=',self.env.user.branch_id.id)
                ], limit=1)          

    tsc_journal_ids = fields.Many2many('account.journal', store=False, readonly=False,
        compute='_compute_tsc_journal_ids')

    @api.depends('journal_id')
    def _compute_tsc_journal_ids(self):
        self.tsc_journal_ids = self.env['account.journal'].search([('type', 'in', ('bank', 'cash')),
                                                                   ('company_id', '=', self.company_id.id),
                                                                   '|', 
                                                                   ('branch_id','=',False),
                                                                   ('branch_id','=',self.env.user.branch_id.id)
        ])
    """




    




