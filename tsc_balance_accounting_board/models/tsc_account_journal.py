# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError

class tsc_AccountJournal(models.Model):

    _name = 'account.journal'
    _inherit = ['account.journal', 'mail.thread']

    tsc_other_currency_balance = fields.Boolean(string="Balance in another currency",
                                               help="Identifies if the accounting journal will show a balance in another currency on the accounting dashboard",
                                               required=False,
                                               readonly=False,
                                               store=True,
                                               copy=False,
                                               tracking=True,
                                               default=False)

    tsc_another_currency_balance_value = fields.Char(string="Balance in another currency value",
                                                     compute="_compute_tsc_another_currency_balance_value")


    def get_journal_dashboard_datas(self):
        res = super(tsc_AccountJournal, self).get_journal_dashboard_datas()
        res.update({
            'tsc_other_currency_balance': self.tsc_other_currency_balance,
            'tsc_another_currency_balance_value': self.tsc_another_currency_balance_value,
        })
        return res

    #@api.onchange()
    @api.depends('tsc_other_currency_balance')
    def _compute_tsc_another_currency_balance_value(self):
        for record in self:
            if record.tsc_other_currency_balance:
                tsc_search_line = self.env['account.move.line'].search([
                        ('journal_id', '=', record.id),
                        ('parent_state', '=', 'posted'),
                        ('account_id', '=', record.default_account_id.id)
                    ])
                tsc_line_sum = 0.00
                tsc_index = 'balance' if record.currency_id != False and record.currency_id.id != self.env.company.currency_id.id else 'amount_currency'
                for tsc_line in tsc_search_line:
                    tsc_line_sum += tsc_line[tsc_index]

                record.tsc_another_currency_balance_value = "{:,.2f}".format(tsc_line_sum)

            else:
                record.tsc_another_currency_balance_value = False





