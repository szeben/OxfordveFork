# -*- coding: utf-8 -*-

from odoo import models, api, fields

class AccountMoveExtension(models.Model):
    
    _inherit = 'account.move'

    def _get_reconciled_vals(self, partial, amount, counterpart_line):
        res = super()._get_reconciled_vals(partial, amount, counterpart_line)
        
        usuario_grupo = self.env.user.has_group('restrictions_for_bank_statements_and_conciliation.group_romper_conciliaciones_extractos_bancarios')
        
        res.update(puede_romper_conciliacion=usuario_grupo)
        return res

    
