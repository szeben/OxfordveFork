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
        return ['|', ('team_id.x_studio_many2one_field_a2jVA', '=', False), ('team_id.x_studio_many2one_field_a2jVA', 'in', [b.id for b in self.env.user.branch_ids])]
