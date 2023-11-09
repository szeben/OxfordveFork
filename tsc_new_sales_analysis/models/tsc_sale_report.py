# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleReport(models.Model):

    _inherit = 'sale.report'

    tsc_oxford_domain = fields.Char(
        compute="_tsc_compute_custom_domain_oxford", search='oxford_branch_ids_search', readonly=True, string="domain")

    def _tsc_compute_custom_domain_oxford(self):
        for record in self:
            record.tsc_oxford_domain = ""

    def oxford_branch_ids_search(self, operator, operand):
        return ['|', ('branch_id', '=', False), ('branch_id', 'in', [b.id for b in self.env.user.branch_ids])]
