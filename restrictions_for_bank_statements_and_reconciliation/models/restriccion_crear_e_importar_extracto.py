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
        u = self.env['res.users'].search([('id', '=', self.env.uid)])
        for g in u.groups_id:
            #xml_id = g.get_metadata()[0].get('xmlid')
            #xml_id = g.get_external_id()
            #raise exceptions.UserError(('No tienes permiso para crear extractos bancarios. %s %s %s') %((self.env.uid),(u.name),(xml_id)))
            if(g.id == 91):
                raise exceptions.UserError(('No tienes permiso para crear extractos bancarios. %s %s %s') %((self.env.uid),(u.name),(g.id)))



        
        return res
    
    def check_create(self):
        """Verificar si el usuario tiene el permiso para crear un extracto bancario.
        """
       
        raise exceptions.UserError(_('You have already sent this badge too many time this month.'))
        return False