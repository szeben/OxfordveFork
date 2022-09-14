# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    overall_stock = fields.Float(
        _("Stock general"),
        compute="_compute_overall_stock",
        store=True,
        readonly=True
    )

    @api.depends("qty_available")
    def _compute_overall_stock(self):
        for product in self:
            product.overall_stock = self.env["product.template"].sudo().browse(
                product.id).qty_available


class ProductProduct(models.Model):
    _inherit = 'product.product'

    overall_stock = fields.Float(
        _("Stock general"),
        compute="_compute_overall_stock",
        store=True,
        readonly=True
    )

    @api.depends("product_tmpl_id.overall_stock")
    def _compute_overall_stock(self):
        for product in self:
            product.overall_stock = product.product_tmpl_id.overall_stock


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    is_main = fields.Boolean(
        string=_("¿Es un almacén principal?"),
    )


class Users(models.Model):
    _inherit = 'res.users'

    def write(self, vals):
        branch_id = vals.get("branch_id")
        if branch_id:
            warehouse = self.env["stock.warehouse"].search(
                [("is_main", "=", True), ("branch_id", "=", branch_id)],
                limit=1
            )
            if warehouse:
                vals["property_warehouse_id"] = warehouse.id
        return super().write(vals)
