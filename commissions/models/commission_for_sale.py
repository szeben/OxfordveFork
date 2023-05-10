# -*- coding: utf-8 -*-

import json
from odoo import tools
from odoo import models, fields, api, exceptions
from datetime import datetime, date,timedelta
from calendar import monthrange
from dateutil.relativedelta import relativedelta


class CommissionForSale(models.Model):
    _name = 'commission.for.sale'
    _description = 'Commission for Sale'

    name = fields.Char(string="Nombre", required=True)
    commission_type = fields.Selection(string='Tipo de comisión', required=True,
                                       selection=[
                                           ('fija', 'Fija'),
                                           ('basada_en_otra_comision', 'Basada en otra Comisión')],
                                       default='fija')

    product_id = fields.Many2one('product.product', string="Producto", required=True)
    categ_id = fields.Many2one(related='product_id.categ_id', string="Categoría", readonly=True)
    cant_minima_base = fields.Float(string='Can. Mín. Base', required=True)
    bono_base = fields.Float(string='Bono Base', required=True)
    basado_en = fields.Many2one('commission.for.sale', string="Basado en", domain="[('id', '!=', id),('product_id', '=', product_id if product_id else False)]")
    cant_min_base_factor_divisor = fields.Float(string='Factor divisor Cant. Mín.', default=1.0)
    cant_min_base_factor_multiplicador = fields.Float(string='Factor multiplicador Cant. Mín.', default=1.0)
    cant_min_base_factor_extra = fields.Float(string='Factor extra Cant. Mín.')
    cant_min_base_otra_com = fields.Float(compute="_compute_cant_min_base_otra_com", string='Cant. Mín. Base - otra comisión', readonly=True, store=True)
    bono_base_factor_divisor = fields.Float(string='Factor divisor Bono B.', default=1.0)
    bono_base_factor_multiplicador = fields.Float(string='Factor multiplicador Bono B.', default=1.0)
    bono_base_factor_extra = fields.Float(string='Factor extra Bono B.')
    bono_base_otra_com = fields.Float(compute="_compute_bono_base_otra_com", string='Bono Base - otra comisión', readonly=True, store=True)

    forma_de_calculo = fields.Selection([
        ('fijo', 'Fijo'),
        ('regla_de_tres', 'Regla de tres')], default='fijo')

    @api.onchange('name')
    def _onchange_product_id(self):
        for record in self:
            if not record.name:
                record.update({
                    'product_id': False,
                    'categ_id': False,
                })
                return
            
            if record.name:
                if record.product_id and record.product_id._origin:
                    record['product_id'] = record.product_id._origin

    @api.onchange('product_id')
    def _onchange_initial_product_id(self):
        for record in self:
            if not record.name:
                record.update({
                    'product_id': False,
                    'categ_id': False,
                })
                return
            
            if record.name:
                if record.product_id and record.product_id._origin:
                    record['product_id'] = record.product_id._origin
    

    @api.constrains('product_id')
    def _existe_commission_in_commission_ids(self):
        for r in self:
            existe_id_comm = []
            existe_nomb_comm = []

            for l in r.product_id.commission_ids:
                
                if l.id in existe_id_comm:
                    raise exceptions.UserError(
                        'El producto tiene una o más comisiones repetidas. Por favor, verifique')
                else:
                    nomb = l.name.lower()                
                    if nomb in existe_nomb_comm:
                        raise exceptions.UserError(
                            'El producto tiene una o más comisiones con nombres repetidos. Por favor, verifique')

                existe_id_comm.append(l.id)
                existe_nomb_comm.append(nomb)
    
    @api.constrains('cant_min_base_factor_divisor')
    def validation_division_by_zero_cant_min(self):
        for r in self:     
            if r.cant_min_base_factor_divisor == 0:            
                    raise exceptions.UserError(
                        'El factor divisor no puede ser cero. Por favor, verifique')

    @api.constrains('bono_base_factor_divisor')
    def validation_division_by_zero_bono_base(self):
        for r in self:     
            if r.bono_base_factor_divisor == 0:            
                    raise exceptions.UserError(
                        'El factor divisor no puede ser cero. Por favor, verifique')
            
            
    def write(self, values):
        res = super(CommissionForSale, self).write(values)
        for r in self:
            existe_id_comm = []
            existe_nomb_comm = []

            for l in r.product_id.commission_ids:
                
                if l.id in existe_id_comm:
                    raise exceptions.UserError(
                        'El producto tiene una o más comisiones repetidas. Por favor, verifique')
                else:
                    nomb = l.name.lower()                
                    if nomb in existe_nomb_comm:
                        raise exceptions.UserError(
                            'El producto tiene una o más comisiones con nombres repetidos. Por favor, verifique')

                existe_id_comm.append(l.id)
                existe_nomb_comm.append(nomb)

        return res
                

    @api.depends("product_id", "name", "commission_type", "bono_base", "cant_min_base_otra_com", "basado_en",
                 "cant_min_base_factor_divisor", "cant_min_base_factor_multiplicador", "cant_min_base_factor_extra",
                 "bono_base_factor_divisor", "cant_min_base_factor_multiplicador", "bono_base_factor_extra")
    def _compute_cant_min_base_otra_com(self):

        for line in self:

            if line.commission_type == 'basada_en_otra_comision' and line.cant_min_base_factor_divisor > 0:

                c = line.basado_en
                if c.commission_type == 'fija':
                    line.cant_min_base_otra_com = ((c.cant_minima_base / line.cant_min_base_factor_divisor) *
                                                   line.cant_min_base_factor_multiplicador) + line.cant_min_base_factor_extra
                else:
                    line.cant_min_base_otra_com = ((c.cant_min_base_otra_com / self.cant_min_base_factor_divisor) *
                                                   line.cant_min_base_factor_multiplicador) + line.cant_min_base_factor_extra

    @api.depends("product_id", "name", "commission_type", "bono_base", "cant_min_base_otra_com", "basado_en",
                 "cant_min_base_factor_divisor", "cant_min_base_factor_multiplicador", "cant_min_base_factor_extra",
                 "bono_base_factor_divisor", "bono_base_factor_multiplicador", "bono_base_factor_extra")
    def _compute_bono_base_otra_com(self):

        for line in self:

            if line.commission_type == 'basada_en_otra_comision' and line.bono_base_factor_divisor > 0:

                c = line.basado_en
                if c.commission_type == 'fija':
                    line.bono_base_otra_com = ((c.bono_base / line.bono_base_factor_divisor) *
                                               line.bono_base_factor_multiplicador) + line.bono_base_factor_extra

                else:
                    line.bono_base_otra_com = ((c.bono_base_otra_com / line.bono_base_factor_divisor) *
                                               line.bono_base_factor_multiplicador) + line.bono_base_factor_extra


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    commission_id = fields.Many2one('commission.for.sale', string="Plantilla del producto")
    total_commissions = fields.Integer(string="Comisiones asociadas")


class ProductProduct(models.Model):
    _inherit = 'product.product'
    commission_id = fields.Many2one('commission.for.sale', string="Comisión")
    commission_ids = fields.One2many('commission.for.sale', 'product_id', string="Productos")
    total_commissions = fields.Integer(compute="_compute_total_commissions", string="Comisiones asociadas", store=True)

    # Comision unica

    @api.constrains('commission_ids')
    def _existe_commission_in_commission_ids(self):
        for r in self:
            existe_id_comm = []
            existe_nomb_comm = []

            for i, l in enumerate(r.commission_ids):
                if l.id in existe_id_comm:
                    raise exceptions.UserError(
                        'El producto tiene una o más comisiones repetidas. Por favor, verifique')
                else:
                    nomb = l.name.lower()
                    if nomb in existe_nomb_comm:
                        raise exceptions.UserError(                
                            'El producto tiene una o más comisiones con nombres repetidos. Por favor, verifique')        
            
                existe_id_comm.append(l.id)
                existe_nomb_comm.append(nomb)    
                       
    
    # def write(self, values):
    #     res = super(ProductProduct, self).write(values)
    #     for r in self:
    #         for c in r.commission_ids:                              
    #             if c.product_id and c.product_id._origin:
    #                     c['product_id'] = c.product_id._origin

    #     return res

    @api.depends("commission_id", "commission_ids")
    def _compute_total_commissions(self):

        for r in self:
            if r.commission_ids:
                if len(r.commission_ids) > 0:
                    if r.id:
                        p_tmpl = r.product_tmpl_id
                        if (p_tmpl.id):
                            p_tmpl['total_commissions'] = len(r.commission_ids)
                            r['total_commissions'] = len(r.commission_ids)
            else:
                p_tmpl = r.product_tmpl_id
                p_tmpl['total_commissions'] = 0
                r.total_commissions = 0


class ProductCategory(models.Model):
    _inherit = 'product.category'
    commission_id = fields.Many2one('commission.for.sale', string="Comisión")


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    commission_id = fields.Many2one('commission.for.sale', string="Comisión")


class CrmTeam(models.Model):
    _inherit = 'crm.team'
    commission_id = fields.Many2one('commission.for.sale', string="Comisión")


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    commission_id = fields.Many2one('commission.for.sale', string="Comisión")
    team_id = fields.Many2one(related='partner_id.team_id', string="Equipo de ventas", readonly=True, store=True)
    collection_id = fields.Many2one(related='account_id.collection_id', string="Cobranza", readonly=True, store=True)
    commission_by_collection = fields.Float(compute="_compute_commission_by_collection", string="Comisión por cobranza", store=True)

    @api.depends(
        "parent_state",
        "date",
        "collection_id",
        "debit",
        "payment_id",
        "move_id"
    )
    def _compute_commission_by_collection(self):
        for line in self:

            if (
                line.parent_state == 'posted'
                and line.date
                and line.collection_id != False
                and line.debit != 0
                and line.partner_id != False
            ):

                line.commission_by_collection = line.debit * line.collection_id.percentage


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    commission_id = fields.Many2one('commission.for.sale', string="Comisión")
    categ_id = fields.Many2one(related='product_id.categ_id', string="Categoría del producto", readonly=True, store=True)
    team_id = fields.Many2one(related='order_id.partner_id.team_id', string="Equipo de ventas", readonly=True, store=True, domain=[('order_id', '!=', False)])
    quantity = fields.Float(string="Cantidad facturada", store=True)
    amount_sale = fields.Monetary(string="Monto de la venta", store=True)
    date = fields.Datetime(related='order_id.date_order', string="Fecha", readonly=True, store=True)
    total_vendidos = fields.Float(compute="_compute_total_vendidos", string="Total vendidos", store=True)
    total_amount_sales = fields.Monetary(compute="_compute_total_vendidos", string="Monto de las ventas", store=True)
    total_amount_commissions = fields.Monetary(compute="_compute_commissions", string="Total de comisión", store=True)

    @api.depends("product_id", "commission_id", "product_id.commission_ids", "order_id", "order_id.date_order",
                 "order_id.invoice_ids", "order_id.state", "invoice_lines", "state", "date", "invoice_status")
    def _compute_total_vendidos(self):
        for line in self.filtered(lambda line: line.invoice_lines):
            if line.invoice_lines:
                line.total_vendidos = 0
                line.total_amount_sales = 0

                if line.order_id and line.order_id.invoice_ids and line.order_id.state == 'done' and line.qty_invoiced > 0:
                    for f in line.order_id.invoice_ids:
                        if f.state == 'posted' and f.move_type == 'out_invoice':
                            cant_f = 0
                            for line_f in f.invoice_line_ids:
                                if line_f.product_id.id == line.product_id.id:
                                    if line.order_id.date_order and not line.date:
                                        line.date = line.order_id.date_order                                                                   
                                    if line.order_id.branch_id and not line_f.branch_id:
                                        line_f.branch_id = line.order_id.branch_id
                                    if line_f.product_uom_id == line_f.product_id.uom_id and line_f.quantity:
                                        cant_f = line_f.quantity
                                    elif line_f.product_uom_id.uom_type == 'bigger':
                                        cant_f = line_f.quantity * (line_f.product_uom_id.factor_inv / line_f.product_id.uom_id.factor_inv)
                                    elif line_f.product_uom_id.uom_type == 'smaller' or line_f.product_uom_id.uom_type == 'reference':
                                        cant_f = line_f.quantity * line_f.product_id.uom_id.factor

                                    line.quantity = cant_f
                                    line.total_vendidos = line.total_vendidos + line.quantity
                                    line.amount_sale = line.order_id.amount_total
                                    line.total_amount_sales = line.total_amount_sales + line.amount_sale

    @api.depends("total_vendidos", 'state', "date", "invoice_lines", "invoice_status", "product_id", "commission_id", "product_id.commission_ids", "product_id.commission_id")
    def _compute_commissions(self):
        for line in self:
            if line.invoice_lines:
                line.total_amount_commissions = 0
                len_lines = 0

                if line.product_id.commission_ids and line.total_vendidos != 0 and line.date and line.team_id:
                    f1 = date(line.date.year, line.date.month, 1)
                    f2 = date(line.date.year, line.date.month, monthrange(line.date.year, line.date.month)[1])

                    lines = self.env['sale.order.line'].search([
                        '&', '&', '&', '&', '&',
                        ('date', '>=', f1),
                        ('date', '<=', f2),
                        ('product_id', '=', line.product_id.id),
                        ('team_id', '=', line.team_id.id),
                        ('total_vendidos', '>', 0),
                        ('product_id.commission_ids', '!=', False)]
                    )

                    if lines:
                        total_vendidos_mes = sum(lines.mapped("total_vendidos"))
                        line_id = line.id
                        len_lines = len(lines)

                        for lin in lines:
                            cumplen_fija_ids = []
                            cumplen_bas_ids = []
                            max_fija_c = False
                            max_bas_c = False
                            comission_max = False
                            line.total_amount_commissions = 0

                            for c in line.product_id.commission_ids:
                                if c.commission_type == 'fija':
                                    if total_vendidos_mes >= c.cant_minima_base:
                                        cumplen_fija_ids.append(c)
                                else:
                                    if total_vendidos_mes >= c.cant_min_base_otra_com:
                                        cumplen_bas_ids.append(c)

                            if cumplen_fija_ids:
                                max_fija_c = max(cumplen_fija_ids, key=lambda x: x.cant_minima_base)

                            if cumplen_bas_ids:
                                max_bas_c = max(cumplen_bas_ids, key=lambda x: x.cant_min_base_otra_com)

                            if cumplen_fija_ids and cumplen_bas_ids:
                                if max_fija_c.cant_minima_base >= max_bas_c.cant_min_base_otra_com:
                                    comission_max = max_fija_c
                                else:
                                    comission_max = max_bas_c

                            elif cumplen_fija_ids:
                                comission_max = max_fija_c

                            elif cumplen_bas_ids:
                                comission_max = max_bas_c

                            line.total_amount_commissions = 0

                            if comission_max and (line.id == line_id):
                                len_lines = len(lines)
                                if comission_max.commission_type == 'fija':
                                    if comission_max.forma_de_calculo == 'fijo':
                                        line.total_amount_commissions = comission_max.bono_base / len_lines

                                    else:
                                        line.total_amount_commissions = (
                                            total_vendidos_mes * comission_max.bono_base / comission_max.cant_minima_base
                                        ) / len_lines

                                elif comission_max.commission_type == 'basada_en_otra_comision':
                                    if comission_max.forma_de_calculo == 'fijo':
                                        line.total_amount_commissions = comission_max.bono_base_otra_com / len_lines

                                    else:
                                        line.total_amount_commissions = (
                                            total_vendidos_mes * comission_max.bono_base_otra_com / comission_max.cant_min_base_otra_com
                                        ) / len_lines

                            else:
                                line.total_amount_commissions = 0


class AccountAccount(models.Model):
    _inherit = 'account.account'
    collection_id = fields.Many2one('configuration.collection', string="Cobranza")


class ConfigurationCollection(models.Model):
    _name = "configuration.collection"
    _description = "Configuración del porcentaje a pagar por las cobranzas realizadas"

    name = fields.Char(string="Nombre", default=" ")
    percentage = fields.Float(string="Porcentaje (%) de comisión", required=True)
    account_ids = fields.Many2many('account.account', 'collection_id', string="Cuentas contables a considerar", required=True, domain="[('user_type_id.id', '=', 3)]")   

    @api.model
    def create(self, vals):
        res = super(ConfigurationCollection, self).create(vals)
        u = self.env['configuration.collection'].search([])
        if u:
            total = len(u)
            for i, record in enumerate(u):
                if record:
                    if i >= 0 and i < total-1:
                        u[i].unlink()
        else:
            return

        u = self.env['configuration.collection'].search([])

        if u:
            for c in u.account_ids:
                c.collection_id = u.id

        return res

    def write(self, values):
        res = super(ConfigurationCollection, self).write(values)
        u = self.env['configuration.collection'].search([('id', '=', self.id)])
        c = self.env['account.account'].search([
            '&',
            ('user_type_id.id', '=', 3),
            ('collection_id', '=', self.id)]
        )
        if c:
            for record in c:
                record.collection_id = False

        if u:
            for cuenta in u.account_ids:
                cuenta.collection_id = u.id

        return res

    @api.constrains('percentage')
    def _validacion_porcentaje(self):
        for r in self:
            if r.percentage < 0:
                if r.percentage < 0:
                    raise exceptions.UserError(
                        'El porcentaje no puede ser un número negativo. Por favor, verifique')


class TeamSaleReport(models.Model):
    _name = "team.sale.report"
    _description = "Reporte de comisiones asignadas"
    _auto = False

    @property
    def _table_query(self):
        select_ = """
            WITH commission_by_sale AS (
                SELECT
                    date,
                    team_id,                             
                    SUM(total_vendidos) AS total_vendidos,
                    SUM(total_amount_sales) AS total_amount_sales,
                    SUM(total_amount_commissions) AS total_amount_commissions,
                    0.0 AS commission_by_collection,
                    0.0 AS debit
                FROM sale_order_line sol
                WHERE
                    sol.order_id IS NOT NULL
                    AND sol.order_partner_id IS NOT NULL                                      
                GROUP BY
                    date,
                    team_id                         
                ORDER BY
                    date
            ),
            commission_by_collection AS (
                SELECT
                    aml.date,
                    aml.team_id,                          
                    0.0 AS total_vendidos,
                    0.0 AS total_amount_sales,
                    0.0 AS total_amount_commissions,
                    SUM(aml.commission_by_collection) AS commission_by_collection,
                    SUM(aml.debit) AS debit
                FROM
                    account_move_line aml
                    LEFT JOIN account_account aa ON (aml.account_id = aa.id)
                WHERE
                    aml.parent_state = 'posted'
                    AND aa.collection_id IS NOT NULL
                    AND aml.debit != 0                    
                    AND aml.partner_id IS NOT NULL               
                GROUP BY
                    aml.date,
                    aml.team_id                              
                ORDER BY date
            )
        SELECT
            ROW_NUMBER() OVER () AS id,
            ucommisions.date,
            ucommisions.team_id,             
            SUM(total_vendidos) AS total_vendidos,
            SUM(total_amount_sales) AS total_amount_sales,
            SUM(total_amount_commissions) AS total_amount_commissions,
            SUM(commission_by_collection) AS commission_by_collection,
            SUM(debit) AS debit,
            SUM(COALESCE(total_amount_commissions, 0) + COALESCE(commission_by_collection, 0)) AS total_commissions
        FROM (
                SELECT *
                FROM
                    commission_by_sale
                UNION ALL
                SELECT *
                FROM
                    commission_by_collection
            ) AS ucommisions
        WHERE
            ucommisions.date IS NOT NULL
        GROUP BY
            ucommisions.team_id,
            ucommisions.date               
        ORDER BY
            ucommisions.team_id,
            ucommisions.date             
        """
        return select_

    date = fields.Datetime(
        string="Fecha",
        readonly=True
    )

    team_id = fields.Many2one(
        'crm.team',
        string="Equipo de ventas", readonly=True
    )

    total_vendidos = fields.Float(
        string="Cantidad de ventas",
        readonly=True
    )
    total_amount_sales = fields.Float(
        string="Monto de las ventas",
        readonly=True
    )
    total_amount_commissions = fields.Float(
        string="Comisión asignada por las ventas",
        readonly=True
    )
    debit = fields.Float(
        string="Monto de la cobranza",
        readonly=True
    )
    commission_by_collection = fields.Float(
        string="Comisión por cobranza",
        readonly=True
    )
    total_commissions = fields.Float(
        string="Total de comisiones asignadas",
        readonly=True
    )
