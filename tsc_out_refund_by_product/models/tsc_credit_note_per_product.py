# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError

class tsc_AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    tsc_move_type = fields.Selection(string='Move Type', related='move_id.move_type', store=True)
    tsc_reversed_entry_id = fields.Many2one(string='Reversal of', related='move_id.reversed_entry_id', store=True)
    tsc_invoice_origin = fields.Char(string='Origin', related='move_id.invoice_origin', store=True)
    tsc_amount_total_in_currency_signed = fields.Monetary(string='Total in Currency Signed', related='move_id.amount_total_in_currency_signed', store=True)
    tsc_payment_state  = fields.Selection(string='Payment Status', related='move_id.payment_state', store=True)
    tsc_team_id  = fields.Many2one(string='Sales Team', related='move_id.team_id', store=True)