# -*- coding: utf-8 -*-

import json
from odoo import tools
from odoo import models, fields, api, exceptions
from datetime import datetime, date
from calendar import monthrange


class CommissionForSale(models.Model):
    _name = 'commission.for.sale'
    _description = 'Commission for Sale'

    name = fields.Char(string="Nombre", required=True)
    commission_type = fields.Selection(string='Tipo de comisión', required=True,
                                       selection=[
                                           ('fija', 'Fija'),
                                           ('basada_en_otra_comision', 'Basada en otra Comisión')],
                                       default='fija')

    product_id = fields.Many2one('product.product', string="Producto", readonly=True)
    categ_id = fields.Many2one(related='product_id.categ_id', string="Categoría del producto", readonly=True)
    product_ids = fields.One2many('product.product', 'commission_id', string="Agrupado con")
    product_templ_id = fields.Many2one('product.template', string="Plantilla del producto", invisible='True')
    agrupated_product_id = fields.Many2one('agrupated.product', string="Producto de agrupated_product_id")
    agrupated_product_ids = fields.One2many('agrupated.product', 'commission_id', string="Agrupado con agrupated.product")
    cant_minima_base = fields.Float(string='Cantidad mínima base', required=True)
    bono_base = fields.Float(string='Bono base', required=True)
    basado_en = fields.Many2one('commission.for.sale', string="Basado en", domain="[('id', '!=', id),('product_id', '=', product_id if product_id else False)]")
    commission_ids = fields.One2many('commission.for.sale', 'id', string="Agrupado con", domain="[('id', '=', id)]")
    cant_min_base_factor_divisor = fields.Float(string='Factor divisor', default=1.0)
    cant_min_base_factor_multiplicador = fields.Float(string='Factor multipicador', default=1.0)
    cant_min_base_factor_extra = fields.Float(string='Factor extra')
    cant_min_base_otra_com = fields.Float(compute="_compute_cant_min_base_otra_com", string='Cantidad mínima base basada en otra comisión', readonly=True, store=True)
    bono_base_factor_divisor = fields.Float(string='Factor divisor', default=1.0)
    bono_base_factor_multiplicador = fields.Float(string='Factor multipicador', default=1.0)
    bono_base_factor_extra = fields.Float(string='Factor extra')
    bono_base_otra_com = fields.Float(compute="_compute_bono_base_otra_com", string='Bono base basado en otra comisión', readonly=True, store=True)

    forma_de_calculo = fields.Selection([
        ('fijo', 'Fijo'),
        ('regla_de_tres', 'Regla de tres')], default='fijo')

    sale_order_id = fields.Many2one('sale.order', string="Venta", readonly=True)
    sale_order_ids = fields.One2many('sale.order', 'commission_id', string='Ventas')
    sale_order_line_id = fields.Many2one('sale.order.line', string="Linea de ventas", readonly=True)
    sale_order_line_ids = fields.One2many('sale.order.line', 'commission_id', string='Líneas de ventas')

    @api.onchange('name')
    def _onchange_product_id(self):
        if not self.name:
            self.update({
                'product_id': False,
                'categ_id': False,
            })
            return

        if self.name:
            if self.product_id and self.product_id._origin:
                self['product_id'] = self.product_id._origin

    @api.depends("product_id", "name", "commission_type", "bono_base", "cant_min_base_otra_com", "basado_en",
                 "cant_min_base_factor_divisor", "cant_min_base_factor_multiplicador", "cant_min_base_factor_extra",
                 "bono_base_factor_divisor", "cant_min_base_factor_multiplicador", "bono_base_factor_extra")
    def _compute_cant_min_base_otra_com(self):

        for line in self:

            if line.commission_type == 'basada_en_otra_comision':

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

            if line.commission_type == 'basada_en_otra_comision':

                c = line.basado_en
                if c.commission_type == 'fija':
                    line.bono_base_otra_com = ((c.bono_base / line.bono_base_factor_divisor) *
                                               line.bono_base_factor_multiplicador) + line.bono_base_factor_extra

                else:
                    line.bono_base_otra_com = ((c.bono_base_otra_com / line.bono_base_factor_divisor) *
                                               line.bono_base_factor_multiplicador) + line.bono_base_factor_extra


class AgrupatedProduct(models.Model):
    _name = 'agrupated.product'
    _description = 'Productos agrupados en una comisión'
    product_id = fields.Many2one('product.product', string="Producto")
    commission_id = fields.Many2one('commission.for.sale', string="Comisión")
    commission_ids = fields.One2many('commission.for.sale', 'product_id', string="Comisión")


class ProductTemplateInherit(models.Model):
    _inherit = 'product.template'
    commission_id = fields.Many2one('commission.for.sale', string="Plantilla del producto")
    commission_ids = fields.One2many('commission.for.sale', 'product_templ_id', string="Plantilla del producto")
    total_commissions = fields.Integer(string="Comisiones asociadas")


class ProductProductInherit(models.Model):
    _inherit = 'product.product'
    product_templ_line_id = fields.Many2one('product.template.commission.line', string="Linea de la plantilla del producto")
    commission_id = fields.Many2one('commission.for.sale', string="Comisión")
    commission_ids = fields.One2many('commission.for.sale', 'product_id', string="Productos")
    agrupated_product_id = fields.Many2one('agrupated.product', string="Producto agrupado")
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
                    nomb = l.name
                    if nomb in existe_nomb_comm:
                        raise exceptions.UserError(
                            'El producto tiene una o más comisiones con nombres repetidos. Por favor, verifique')

                existe_id_comm.append(l.id)
                existe_nomb_comm.append(nomb)

    @api.depends("commission_id", "commission_ids")
    def _compute_total_commissions(self):

        for r in self:
            if len(r.commission_ids) > 0:
                if r.id == self.id:
                    p_tmpl = self.product_tmpl_id
                    if (p_tmpl.id):
                        p_tmpl['total_commissions'] = len(r.commission_ids)
                        self['total_commissions'] = len(r.commission_ids)


class ProductCategoryInherit(models.Model):
    _inherit = 'product.category'
    commission_id = fields.Many2one('commission.for.sale', string="Comisión")


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'
    commission_id = fields.Many2one('commission.for.sale', string="Comisión")


class CrmTeamInherit(models.Model):
    _inherit = 'crm.team'
    commission_id = fields.Many2one('commission.for.sale', string="Comisión")
    total_commission = fields.Float(string="Total comisión del vendedor")


class AccountMoveLineInherit(models.Model):
    _inherit = 'account.move.line'
    commission_id = fields.Many2one('commission.for.sale', string="Comisión")
    team_id = fields.Many2one(related='move_id.team_id', string="Equipo de ventas", readonly=True, store=True)
    payment_state = fields.Selection(related='move_id.payment_state', string="Estado del pago", readonly=True, store=True)
    #cobranza_id = fields.Many2one('configuration.cobranza', string="Configuración de cobranza")
    
    #cobranza_account_id = fields.Many2one(realated='cobranza_id.account_id', string="Cuenta de cobranza")

    #account_id_domain = fields.Char(
        #compute="_compute_account_id_domain",
        #readonly=True,
       # store=True,
   # )

   # @api.depends('account_id')
   # def _compute_account_id_domain(self):
       # print("ESTOYE N CALCULAR DOMINIO")
        #for rec in self:
           # list = self.env['configuration.cobranza'].search([])
           # print("ESTA ES LA LISTAaaaaaaaaaaaaaaa", list)
           # return {'domain': {'account_id': [('account_id', 'in', [c.account_id.id for c in list])]}}
            #rec.account_id_domain = json.dumps([('account_id', 'in', [c.account_id.id for c in list])]
            #)


class SaleOrderLineInherit(models.Model):
    _inherit = 'sale.order.line'

    commission_id = fields.Many2one('commission.for.sale', string="Comisión")
    categ_id = fields.Many2one(related='product_id.categ_id', string="Categoría del producto", readonly=True, store=True)

    team_id = fields.Many2one(related='order_id.team_id', string="Equipo de ventas", readonly=True, store=True)
    # branch_id = fields.Many2one(related='order_id.branch_id', string="Ramaaaaa", readonly=True, store=True)
    quantity = fields.Float(string="cantidad facturada", store=True)
    date = fields.Date(string="Fecha de la factura", readonly=True)
    total_vendidos = fields.Float(compute="_compute_total_vendidos", string="Total vendidos", store=True)
    total_amount_commissions = fields.Float(compute="_compute_commissions", string="Total de comisión", store=True)

    @api.depends("product_id", "commission_id", "product_id.commission_ids", "order_id", "order_id.date_order",
                 "order_id.invoice_ids", "order_id.state", "invoice_lines", "state", "date", "invoice_status")
    def _compute_total_vendidos(self):
        for line in self.filtered(lambda line: line.invoice_lines):
            v = line.order_id
            line.total_vendidos = 0

            if v.invoice_ids:
                for f in v.invoice_ids:
                    if f.state == 'posted' and f.move_type == 'out_invoice':
                        for line_f in f.invoice_line_ids:
                            if line_f.product_id.id == line.product_id.id:
                                line.date = f.invoice_date
                                if line.order_id.team_id:
                                    line_f.team_id = line.order_id.team_id
                                line_f.branch_id = line.order_id.branch_id

                                if line_f.product_uom_id == line_f.product_id.uom_id:
                                    cant_f = line_f.quantity
                                elif line_f.product_uom_id.uom_type == 'bigger':
                                    cant_f = line_f.quantity * (line_f.product_uom_id.factor_inv / line_f.product_id.uom_id.factor_inv)
                                elif line_f.product_uom_id.uom_type == 'smaller' or line_f.product_uom_id.uom_type == 'reference':
                                    cant_f = line_f.quantity * line_f.product_id.uom_id.factor

                                line.quantity = cant_f
                                line.total_vendidos = line.total_vendidos + line.quantity

    @api.depends("total_vendidos", "date", "invoice_lines", "invoice_status", "product_id", "commission_id", "product_id.commission_ids", "product_id.commission_id")
    def _compute_commissions(self):
        for line in self:
            if not line.invoice_lines:
                continue

            line.total_amount_commissions = 0

            if line.product_id.commission_ids and line.total_vendidos != 0 and line.date:
                f1 = date(line.date.year, line.date.month, 1)
                f2 = date(line.date.year, line.date.month, monthrange(line.date.year, line.date.month)[1])

                lines = self.env['sale.order.line'].search([
                    '&', '&', '&',
                    ('date', '>=', f1),
                    ('date', '<=', f2),
                    ('product_id', '=', line.product_id.id),
                    ('team_id', '=', line.team_id.id)]
                )

                if lines:
                    total_vendidos_mes = sum(lines.mapped("total_vendidos"))
                    line_id = line.id

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


class AccountAccountInherit(models.Model):
    _inherit = 'account.account'
    cobranza_id = fields.Many2one('configuration.cobranza', string="Cuenta")


class ConfigurationCobranza(models.Model):
    _name = "configuration.cobranza"
    _description = "Configuración del porcentaje a pagar por las cobranzas realizadas"

    name = fields.Char(string="Nombre", default=" ")
    percentage = fields.Float(string="Porcentaje (%) de comisión", required=True)
    account_ids = fields.Many2many('account.account', 'cobranza_id', string="Cuentas contables a considerar", required=True, domain="[('user_type_id.id', '=', 3)]")
    
    @api.model
    def create(self, vals):
        res = super(ConfigurationCobranza, self).create(vals)
        u = self.env['configuration.cobranza'].search([])
        if u:
            total = len(u)
            for i, record in enumerate(u):
                if record:
                    if i >= 0 and i < total-1:
                        u[i].unlink()
        else:
            return
        return res