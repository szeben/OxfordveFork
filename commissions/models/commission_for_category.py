# -*- coding: utf-8 -*-

from odoo import _, api, exceptions, fields, models


class CommissionForCategory(models.Model):
    _name = 'commission.for.category'
    _description = 'Commission for category'
    _inherit = 'commission.commission'

    categ_id = fields.Many2one(
        'product.category',
        string="Categoría",
        required=True,
    )
    basado_en = fields.Many2one(
        comodel_name='commission.for.category',
        domain="[('id', '!=', id), ('categ_id', '=', categ_id)]"
    )

    _sql_constraints = [
        (
            'unique_categ_id_and_commission_id',
            'UNIQUE(categ_id, id)',
            'La categoria tiene una o más comisiones repetidas. Por favor, verifique'
        ),
    ]

    # @api.onchange('categ_id')
    # def _onchange_categ_id(self):
    #     for commission in self:
    #         categ_id = self.env.context.get('default_categ_id')

    #         if categ_id:
    #             categ_id = categ_id
    #         elif (
    #             commission.categ_id
    #             and isinstance(commission.categ_id.id, models.NewId)
    #             and commission.categ_id._origin
    #         ):
    #             categ_id = commission.categ_id._origin.id

    #         if categ_id:
    #             commission.categ_id = categ_id
    #             commission.update({'categ_id': categ_id})
