# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleReport(models.Model):

    _inherit = 'sale.report'

    tsc_custom_domain_oxford = fields.Char(
        compute="_tsc_compute_custom_domain_oxford", search='oxford_branch_ids_search')

    @api.depends('branch_id')
    def _tsc_compute_custom_domain_oxford(self):
        print('computed')

    def oxford_branch_ids_search(self, operator, operand):
        return ['|', ('branch_id', '=', False), ('branch_id', 'in', [b.id for b in self.env.user.branch_ids])]
