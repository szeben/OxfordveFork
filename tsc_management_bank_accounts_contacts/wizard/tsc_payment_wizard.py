# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import UserError

class tsc_PaymentRegisterExtension(models.TransientModel):
    
    _name = 'account.payment.register'
    _inherit = ['account.payment.register', 'mail.thread', 'mail.activity.mixin']
    tsc_partner_bank_id = fields.Many2one(
                                            comodel_name='res.partner.bank',
                                            string="Client Bank Account",
                                            readonly=False,
                                            store=True,
                                            domain="[('id', 'in', tsc_available_partner_bank_ids)]",
                                        )

    tsc_available_partner_bank_ids = fields.Many2many(
        comodel_name='res.partner.bank',
        compute='_compute_tsc_available_partner_bank_ids',
    )

    tsc_move_type = fields.Boolean(string="Account Move Type", 
                                  compute='_compute_tsc_move_type')

    
    @api.depends('can_edit_wizard')
    def _compute_tsc_move_type(self):
        for wizard in self:
            wizard.tsc_move_type = False
            tsc_context_ids = self._context.get('active_ids', [])
            if wizard.can_edit_wizard:
                tsc_account_move = self.env['account.move'].browse(tsc_context_ids)
                tsc_account_move_types = [tsc_type["move_type"] for tsc_type in tsc_account_move]
                wizard.tsc_move_type = tsc_account_move_types in ['out_refund', 'in_refund']

            
    @api.depends('can_edit_wizard')
    def _compute_tsc_available_partner_bank_ids(self):
        for wizard in self:
            if wizard.can_edit_wizard:
                wizard.tsc_available_partner_bank_ids = self.env['res.partner.bank'].search([
                        ('partner_id', '=', wizard.partner_id.id),
                        ])
            else:
                wizard.tsc_available_partner_bank_ids = None

    def _create_payment_vals_from_wizard(self):
        res = super()._create_payment_vals_from_wizard()
        res.update({
            'tsc_partner_bank_id': self.tsc_partner_bank_id.id, 
            'tsc_available_partner_bank_ids': self.tsc_available_partner_bank_ids.ids 
        })
        return res

            

    
    
   