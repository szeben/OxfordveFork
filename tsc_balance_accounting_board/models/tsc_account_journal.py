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
                        ('parent_state', '=', 'posted'),
                        ('account_id', '=', record.default_account_id.id)
                    ])
                tsc_line_sum = 0.000
                tsc_index = 'amount_currency' if record.currency_id.id == False or record.currency_id.id == self.env.company.currency_id.id else 'balance'
                
                for tsc_line in tsc_search_line:
                    tsc_line_sum += tsc_line[tsc_index]

                tsc_new_float = "{:,.3f}".format(tsc_line_sum)
                lang=self.env.user.lang

                if lang.startswith("es"):
                    tsc_new_float = tsc_new_float.replace('.', 'x')
                    tsc_new_float = tsc_new_float.replace(',', '.')
                    tsc_new_float = tsc_new_float.replace('x', ',')

                record.tsc_another_currency_balance_value = tsc_new_float

            else:
                record.tsc_another_currency_balance_value = False





