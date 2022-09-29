# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountBankStatementInherit(models.Model):
     _name = 'account.bank.statement.inherit'
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
             g = self.env['res.groups'].search([('id', 'in', self.user_id.groups_id)])
             raise UserError(('El valor del grupo %s') %(g.id))

             
             # Then call super to execute the parent method
             return super().create(vals)
