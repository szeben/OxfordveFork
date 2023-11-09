# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError

class tsc_AccountJournal(models.Model):

    _name = 'account.journal'
    _inherit = ['account.journal', 'mail.thread']

    tsc_other_currency_balance = fields.Many2one(string="Balance in another currency",
                                               help="Identifies if the accounting journal will show a balance in another currency on the accounting dashboard",
                                               comodel_name="res.currency",
                                               required=False,
                                               readonly=False,
                                               store=True,
                                               copy=False,
                                               tracking=True,
                                               domain=[('active','=',True)], 
                                               default=False)
    
    tsc_other_currency_balance_symbol = fields.Char(string="Balance in another currency symbol",
                                                    related="tsc_other_currency_balance.symbol")

    tsc_another_currency_balance_value = fields.Char(string="Balance in another currency value",
                                            compute="tsc_compute_tsc_another_currency_balance_value")

    
    def get_journal_dashboard_datas(self):
        res = super(tsc_AccountJournal, self).get_journal_dashboard_datas()
        res.update({
            'tsc_other_currency_balance': self.tsc_other_currency_balance.id != False,
            'tsc_another_currency_balance_value': self.tsc_another_currency_balance_value,
            'tsc_other_currency_balance_symbol': self.tsc_other_currency_balance_symbol,
        })
        return res

    @api.depends('tsc_other_currency_balance')
    def tsc_compute_tsc_another_currency_balance_value(self):
        
        for record in self:
            if record.tsc_other_currency_balance.id != False:
                tsc_search_line = self.env['account.move.line'].search([
                        ('parent_state', '=', 'posted'),
                        ('account_id', '=', record.default_account_id.id)
                    ])
                
                tsc_line_sum = sum(tsc_line['amount_currency'] for tsc_line in tsc_search_line)

                if record.currency_id.id != False and record.currency_id.id != self.env.company.currency_id.id:
                    
                    tsc_rate = 0
                    if record.tsc_other_currency_balance.id == self.env.company.currency_id.id:
                        tsc_rate = self.env['res.currency.rate'].search([('currency_id.id', '=', record.currency_id.id)], limit=1).rate                    
                    else:
                        tsc_rate = self.env['res.currency.rate'].search([('currency_id.id', '=', record.tsc_other_currency_balance.id)], limit=1).rate     
                    if tsc_rate:
                        tsc_line_sum = tsc_line_sum / tsc_rate

               
                tsc_new_float = "{:,.3f}".format(tsc_line_sum)
                lang=self.env.user.lang

                if lang.startswith("es"):
                    tsc_new_float = tsc_new_float.replace('.', 'x')
                    tsc_new_float = tsc_new_float.replace(',', '.')
                    tsc_new_float = tsc_new_float.replace('x', ',')
               

                record.tsc_another_currency_balance_value = tsc_new_float

            else:
                record.tsc_another_currency_balance_value = False

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        domain = domain or []
        tsc_search_default_dashboard = self.env.context.get('search_default_dashboard')
        if tsc_search_default_dashboard == 1:
            domain.extend(['|', ('branch_id','=',False),
                       ('branch_id','=',self.env.user.branch_id.id)])
        return super(tsc_AccountJournal, self).search_read(domain, fields, offset, limit, order)






