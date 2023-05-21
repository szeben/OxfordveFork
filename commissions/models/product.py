# -*- coding: utf-8 -*-

from odoo import _, api, exceptions, fields, models


class ProductCategory(models.Model):
    _inherit = 'product.category'

    commission_id = fields.Many2one(
        'commission.for.sale',
        string="Comisión"
    )


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    commission_id = fields.Many2one(
        'commission.for.sale',
        string="Plantilla del producto",
        # related='product_id.commission_id',
        store=True
    )
    total_commissions = fields.Integer(
        string="Comisiones asociadas",
        # related='commission_id.total_commissions',
        store=True
    )


class ProductProduct(models.Model):
    _inherit = 'product.product'

    commission_id = fields.Many2one(
        'commission.for.sale',
        string="Comisión"
    )
    commission_ids = fields.One2many(
        'commission.for.sale',
        'product_id',
        string="Productos"
    )
    total_commissions = fields.Integer(
        compute="_compute_total_commissions",
        string="Comisiones asociadas",
        store=True
    )

    @api.depends("commission_ids")
    def _compute_total_commissions(self):
        for product_id in self:
            product_id.total_commissions = len(product_id.commission_ids.ids)
