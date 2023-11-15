# -*- coding: utf-8 -*-

from odoo import _, api, exceptions, fields, models


class ProductCategory(models.Model):
    _inherit = 'product.category'

    commission_ids = fields.One2many(
        'commission.for.category',
        'categ_id',
        string="Comisiones"
    )


class ProductProduct(models.Model):
    _inherit = 'product.product'

    commission_ids = fields.One2many(
        'commission.for.sale',
        'product_id',
        string="Comisiones"
    )
    commission_group_id = fields.Many2one(
        'commission.group',
        string="Grupo de comisiones",
    )
    total_commissions = fields.Integer(
        compute="_compute_total_commissions",
        string="Comisiones asociadas",
        store=True
    )
    commission_by_category = fields.Boolean(
        string="¿Tiene comisión por categoria?",
        default=True,
    )

    def check_is_commission_or_group(self):
        for product_id in self:
            if product_id.commission_ids and product_id.commission_group_id:
                raise exceptions.ValidationError(
                    "No puede tener comisiones asociadas y un grupo de comisiones"
                )

    @api.onchange("commission_ids", "commission_group_id")
    def _onchange_commissions(self):
        self.check_is_commission_or_group()

    @api.constrains("commission_ids", "commission_group_id")
    def _check_commissions(self):
        self.check_is_commission_or_group()

    @api.constrains("commission_group_id")
    def _check_commission_group_id(self):
        for product_id in self:
            product_ids = product_id.commission_group_id.product_ids
            if product_ids.ids and len(
                set(product_ids.mapped("categ_id").ids).union((product_id.categ_id.id,))
            ) > 1:
                raise exceptions.ValidationError(
                    "El grupo de comisiones no puede tener productos de diferentes categorías"
                )

    @api.depends("commission_ids", "commission_group_id", "commission_group_id.commission_ids")
    def _compute_total_commissions(self):
        for product_id in self:
            if self.commission_group_id:
                commission_ids = self.commission_group_id.commission_ids.ids
            else:
                commission_ids = self.commission_ids.ids
            product_id.total_commissions = len(commission_ids)

    def compute_commission(self, total_sales_amount):
        self.ensure_one()

        commission_ids = (self.commission_group_id or self).commission_ids
        max_commission = max(
            filter(
                lambda x: total_sales_amount >= x.base_min_qty,
                commission_ids
            ),
            default=None,
            key=lambda x: x.base_min_qty,
        )

        if max_commission:
            return max_commission.compute_commission(total_sales_amount)

        return 0.0


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    commission_ids = fields.Many2many(
        'commission.for.sale',
        string="Comisiones",
        compute="_compute_commissions",
        store=True
    )
    commission_group_ids = fields.Many2many(
        'commission.group',
        string="Grupos de comisiones",
        compute="_compute_commissions",
        store=True
    )
    total_commissions = fields.Integer(
        string="Comisiones asociadas",
        compute="_compute_commissions",
        store=True
    )

    @api.depends(
        "product_variant_ids",
        "product_variant_ids.commission_ids",
        "product_variant_ids.commission_group_ids",
        "product_variant_ids.commission_group_ids.commission_ids",
    )
    def _compute_commissions(self):
        for product_template_id in self:
            product_ids = product_template_id.product_variant_ids
            commision_group_ids = product_ids.commission_group_ids

            product_template_id.commission_ids = product_ids.commission_ids
            product_template_id.commission_group_ids = commision_group_ids

            product_template_id.total_commissions = (
                len(product_ids.commission_ids.ids) + len(commision_group_ids.commission_ids.ids)
            )
