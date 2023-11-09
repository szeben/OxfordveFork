# -*- coding: utf-8 -*-

from odoo import _, api, exceptions, fields, models


class CommissionForSale(models.Model):
    _name = 'commission.for.sale'
    _description = 'Commission for Sale'
    _inherit = 'commission.commission'

    product_id = fields.Many2one(
        'product.product',
        string="Producto",
        required=True
    )
    categ_id = fields.Many2one(
        related='product_id.categ_id',
        string="Categoría",
        readonly=True
    )
    basado_en = fields.Many2one(
        comodel_name='commission.for.sale',
        domain="[('id', '!=', id), ('product_id', '=', product_id)]"
    )

    _sql_constraints = [
        (
            'unique_product_id_and_commission_id',
            'UNIQUE(product_id, id)',
            'El producto tiene una o más comisiones repetidas. Por favor, verifique'
        ),
    ]

    @api.constrains('product_id', 'name')
    def _check_unique_product_id_and_insensitive_commission_name(self):
        for record in self:
            if self.search_count([
                ('product_id', '=', record.product_id.id),
                ('name', 'ilike', record.name),
                ('id', '!=', record.id)
            ]) > 0:
                raise exceptions.ValidationError(
                    'El producto tiene una o más comisiones con '
                    'nombres repetidos. Por favor, verifique'
                )

    @api.onchange('product_id')
    def _onchange_product_id(self):
        for commission in self:
            product_id = self.env.context.get('default_product_id')

            if product_id:
                product_id = product_id
            elif (
                commission.product_id
                and isinstance(commission.product_id.id, models.NewId)
                and commission.product_id._origin
            ):
                product_id = commission.product_id._origin.id

            if product_id:
                commission.product_id = product_id
                commission.update({'product_id': product_id})
