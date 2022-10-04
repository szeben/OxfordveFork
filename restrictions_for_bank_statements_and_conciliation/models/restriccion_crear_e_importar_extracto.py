# -*- coding: utf-8 -*-

from odoo import api, exceptions, fields, models


class AccountBankStatementInherit(models.Model):
    _inherit = 'account.bank.statement'

    @api.model
    def create(self, vals):

        res = super(AccountBankStatementInherit, self).create(vals)
        u = self.env['res.users'].search([('id', '=', self.env.uid)])
        if(not u.has_group('restrictions_for_bank_statements_and_conciliation.group_crear_e_importar_extractos_bancarios')):
            raise exceptions.UserError(
                'No tienes permiso para crear extractos bancarios.')

        return res
