# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    @api.constrains('order_line')
    def _existe_producto_in_order_line(self):
        for r in self:
            existe_prod = []

            for i, l in enumerate(r.order_line):

                if l.product_id.id in existe_prod:

                    if r.state == 'draft' or r.state == 'sent':
                        # pass
                        raise exceptions.UserError(
                            'El presupuesto tiene uno o más productos repetidos de variante. Por favor, verifique.')
                    else:
                        if r.state == 'sale':
                          # pass
                            raise exceptions.UserError(
                                'El pedido de venta tiene uno o más productos repetidos de variante. Por favor, verifique.')

                existe_prod.append(l.product_id.id)