# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    branch_id = fields.Many2one('res.branch', string="Branch")


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.model
    def default_get(self, default_fields):
        res = super(AccountMove, self).default_get(default_fields)
        move_type = self.move_type or res.get("move_type")
        if move_type in {'out_invoice', 'out_refund', 'out_receipt'}:
            branch_id = res.get("branch_id")
            if branch_id and (not self.journal_id or self.journal_id.branch_id.id != branch_id):
                journal = self.env["account.journal"].search(
                    [("branch_id", "=", branch_id)], limit=1)
                if journal:
                    res.update({"journal_id": journal.id})
        return res

    @api.model
    def _create(self, data_list):
        for data in data_list:
            stored = data["stored"]
            if stored.get("move_type") in {'out_invoice', 'out_refund', 'out_receipt'}:
                branch_id = stored.get("branch_id")
                if branch_id:
                    journal = self.env["account.journal"].search(
                        [("branch_id", "=", branch_id)], limit=1)
                    if journal.id:
                        stored["journal_id"] = journal.id
        return super()._create(data_list)


class ProductTemplateIn(models.Model):
    _inherit = 'product.template'

    @api.model
    def default_get(self, default_fields):
        res = super(ProductTemplateIn, self).default_get(default_fields)
        if "branch_id" in res:
            res.pop("branch_id", None)
        return res
