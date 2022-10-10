# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions


class AccountBankStatementInherit(models.Model):
    _inherit = 'account.bank.statement'

    @api.model
    def create(self, vals):

        res = super(AccountBankStatementInherit, self).create(vals)
        u = self.env['res.users'].search([('id', '=', self.env.uid)])
        if not u.has_group('restrictions_for_bank_statements_and_conciliation.group_crear_e_importar_extractos_bancarios'):
            raise exceptions.UserError(
                'No tienes permiso para crear extractos bancarios.')

        return res


class AccountMoveLineInherit(models.Model):
    _inherit = "account.move.line"

    @api.model
    def action_reconcile(self):
        res = super(AccountMoveLineInherit, self).action_reconcile()
        u = self.env['res.users'].search([('id', '=', self.env.uid)])
        if not u.has_group('restrictions_for_bank_statements_and_conciliation.group_conciliar_extractos_bancarios'):
            raise exceptions.UserError(
                'No tienes permiso para conciliar extractos bancarios.')

        return res


class AccountAccountInherit(models.Model):
    _inherit = "account.account"

    @api.model
    def action_open_reconcile(self):
        res = super(AccountAccountInherit, self).action_open_reconcile()
        u = self.env['res.users'].search([('id', '=', self.env.uid)])
        if not u.has_group('restrictions_for_bank_statements_and_conciliation.group_conciliar_extractos_bancarios'):
            raise exceptions.UserError(
                'No tienes permiso para conciliar extractos bancarios.')
        return res


class AccountReportInherit(models.AbstractModel):
    _inherit = "account.report"

    @api.model
    def action_partner_reconcile(self, options, params):
        res = super(AccountReportInherit, self).action_partner_reconcile(
            options, params)
        u = self.env['res.users'].search([('id', '=', self.env.uid)])
        if not u.has_group('restrictions_for_bank_statements_and_conciliation.group_conciliar_extractos_bancarios'):
            raise exceptions.UserError(
                'No tienes permiso para conciliar extractos bancarios.')
        return res


class AccountReconciliationInherit(models.AbstractModel):
    _inherit = 'account.reconciliation.widget'

    @api.model
    def get_move_lines_for_manual_reconciliation(self, account_id, partner_id=False, excluded_ids=None, search_str=False, offset=0, limit=None, target_currency_id=False):
        res = super(AccountReconciliationInherit, self).get_move_lines_for_manual_reconciliation(
            account_id, partner_id=False, excluded_ids=None, search_str=False, offset=0, limit=None, target_currency_id=False)
        u = self.env['res.users'].search([('id', '=', self.env.uid)])
        if not u.has_group('restrictions_for_bank_statements_and_conciliation.group_conciliar_extractos_bancarios'):
            raise exceptions.UserError(
                'No tienes permiso para conciliar extractos bancarios.')
        return res
