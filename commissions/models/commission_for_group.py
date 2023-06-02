# -*- coding: utf-8 -*-

from odoo import _, api, exceptions, fields, models


class CommissionGroup(models.Model):
    _name = 'commission.group'
    _description = 'Group of commissions'

    name = fields.Char(string="Nombre", required=True)
    commission_ids = fields.One2many(
        'commission.for.group',
        'group_id',
        string="Comisiones",
        required=True
    )
    product_ids = fields.One2many(
        'product.product',
        'commission_group_id',
        string="Productos",
    )
    total_commissions = fields.Integer(
        compute="_compute_total_commissions",
        string="Comisión total",
    )

    @api.depends('commission_ids')
    def _compute_total_commissions(self):
        for group in self:
            group.total_commissions = len(group.commission_ids.ids)


class CommissionForGroup(models.Model):
    _name = 'commission.for.group'
    _description = 'Commission for Group'
    _inherit = 'commission.commission'

    categ_id = fields.Many2one(
        'product.category',
        string="Categoría",
        compute="_compute_categ_id",
        store=True
    )
    group_id = fields.Many2one(
        'commission.group',
        string="Grupo",
        required=True
    )
    basado_en = fields.Many2one(
        comodel_name='commission.for.group',
        domain="[('id', '!=', id), ('group_id', '=', group_id)]"
    )

    _sql_constraints = [
        (
            'unique_group_id_and_commission_id',
            'UNIQUE(group_id, id)',
            'El grupo tiene una o más comisiones repetidas. Por favor, verifique'
        ),
    ]

    @api.onchange('group_id')
    def _onchange_group_id(self):
        for commission in self:
            group_id = self.env.context.get('default_group_id')

            if group_id:
                group_id = group_id
            elif (
                commission.group_id
                and isinstance(commission.group_id.id, models.NewId)
                and commission.group_id._origin
            ):
                group_id = commission.group_id._origin.id

            if group_id:
                commission.group_id = group_id
                commission.update({'group_id': group_id})

    @api.depends('group_id', 'group_id.product_ids', 'group_id.product_ids.categ_id')
    def _compute_categ_id(self):
        for commission in self:
            if commission.group_id and commission.group_id.product_ids:
                commission.categ_id = commission.group_id.product_ids[0].mapped('categ_id')
            else:
                commission.categ_id = False
