# -*- coding: utf-8 -*-

from odoo import _, api, exceptions, fields, models
from odoo.exceptions import UserError

class TSCAccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    @api.depends('company_id')
    def tsc_journal_domain(self):
        res_user = self.env['res.users'].search([('id', '=', self._uid)])

        if res_user.has_group('tsc_control_cash_payments.tsc_make_cash_payment_group'):
            options = "[('company_id', '=', company_id),('type', 'in', ('bank', 'cash'))]"
        else:
            options = "[('company_id', '=', company_id),('type', '=', 'bank')]"

        return options

    journal_id = fields.Many2one('account.journal', store=True, readonly=False,
        compute='_compute_journal_id',
        domain=tsc_journal_domain,)

class TSCAccountPayment(models.Model):
    _inherit = 'account.payment'

    tsc_check_user_group = fields.Boolean(
        string="Revisa el grupo del usuario activo",
        compute="_compute_tsc_check_user_group",
        store=False
    )

    @api.depends('state')
    def _compute_tsc_check_user_group(self):
        res_user = self.env['res.users'].search([('id', '=', self._uid)])

        if res_user.has_group('tsc_control_cash_payments.tsc_make_cash_payment_group'):
            self.tsc_check_user_group = True
        else:
            self.tsc_check_user_group = False