# -*- coding: utf-8 -*-


from odoo import models, fields, api, exceptions


class AccountBankStatementInherit(models.Model):
    _inherit = 'account.bank.statement'
#     _description = 'name.name'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#    @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100

    @api.model
    def create(self, vals):
    
        
        res = super(AccountBankStatementInherit,self).create(vals)
        g = self.env['res.groups'].search([('id', 'in', self.user_id.groups_id)])

        raise exceptions.UserError(('No tienes permiso para crear extractos bancarios. %s') %(self.journal_id.name))
        return res
    
    def check_create(self):
        """Verificar si el usuario tiene el permiso para crear un extracto bancario.
        """
       
        raise exceptions.UserError(_('You have already sent this badge too many time this month.'))
        return False