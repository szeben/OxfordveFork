# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class tsc_AccountPayment(models.Model):
    
    _name = 'account.payment'
    _inherit = ['account.payment', 'mail.thread', 'mail.activity.mixin']
    
    tsc_partner_bank_id = fields.Many2one('res.partner.bank', 
                                          string="Client Bank Account",
                                          readonly=False, store=True, tracking=True,
                                          #compute='_compute_tsc_partner_bank_id',
                                          domain="[('id', 'in', tsc_available_partner_bank_ids)]",
                                          check_company=True)
    
    tsc_available_partner_bank_ids = fields.Many2many(
        comodel_name='res.partner.bank',
        compute='_compute_tsc_available_partner_bank_ids',
    )

    @api.depends('tsc_available_partner_bank_ids')
    def _compute_tsc_partner_bank_id(self):
        for pay in self:
            pay.tsc_partner_bank_id = pay.tsc_available_partner_bank_ids[:1]._origin

    @api.depends('partner_id')
    def _compute_tsc_available_partner_bank_ids(self):
        for pay in self:
            pay.tsc_available_partner_bank_ids = self.env['res.partner.bank'].search([
                        ('partner_id', '=', pay.partner_id.id),
                        ])





