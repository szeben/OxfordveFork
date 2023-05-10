# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import UserError

class BranchExtension(models.Model):
    _inherit = "res.branch"

    abbrv = fields.Char("Abreviatura", size=3, required=True)
    seq_stock_batch = fields.Char(string="Secuencia para Agrupación de Albaranes")
    seq_stock_package = fields.Char(string="Secuencia para Paquetes")
    seq_sale = fields.Char(string="Secuencia para Sale")

    @api.onchange('abbrv')
    def set_abbrv(self): 
        if self.abbrv:
            val = self.abbrv
            self.abbrv = val.upper()
            
            
            
            
    
    @api.model
    def create(self, vals):

        branch_name = vals.get('name', '')
        branch_abbrv = vals.get('abbrv', '')
        branch_list_abbrvs = ['stock.batch.', 'stock.package.', 'sale.order.']
        branch_list_abbrvs = [x+branch_abbrv for x in branch_list_abbrvs]      
        
        temp_abbrvs = self.env['ir.sequence'].search([('code','in',branch_list_abbrvs)])
        
        if temp_abbrvs:
            raise UserError('La abreviatura coincide con una secuencia existente.')
        else:
            vals['seq_stock_batch'] = self.env['ir.sequence'].create({
                'name': f'{branch_name} SECUENCIA PARA AGRUPACIÓN DE ALBARANÉS: {branch_abbrv}',
                'implementation': 'standard',
                'code': f'stock.batch.{branch_abbrv}',
                'active': True,
                'prefix': f'{branch_abbrv}',
                'padding': 5,
                'number_next': 1,
                'number_increment': 1,
                }).code   

            vals['seq_stock_package'] = self.env['ir.sequence'].create({
                'name': f'{branch_name} SECUENCIA PARA PAQUETES: {branch_abbrv}',
                'implementation': 'standard',
                'code': f'stock.package.{branch_abbrv}',
                'active': True,
                'prefix': f'{branch_abbrv}',
                'padding': 5,
                'number_next': 1,
                'number_increment': 1,
                }).code   

            vals['seq_sale'] = self.env['ir.sequence'].create({
                'name': f'{branch_name} SECUENCIA PARA VENTA: {branch_abbrv}',
                'implementation': 'standard',
                'code': f'sale.order.{branch_abbrv}',
                'active': True,
                'prefix': f'{branch_abbrv}',
                'padding': 5,
                'number_next': 1,
                'number_increment': 1,
                }).code  
            
        return super().create(vals)
    
   
    def write(self, vals):
        
        branch_abbrv = vals.get('abbrv', '')
        
        if branch_abbrv != '' and branch_abbrv != self.abbrv:
            
            branch_name = vals.get('name', self.name)
            branch_list_abbrvs = ['stock.batch.', 'stock.package.', 'sale.order.']
            branch_list_abbrvs = [x+branch_abbrv for x in branch_list_abbrvs]      
            temp_batch = self.env['ir.sequence'].search([('code','in',branch_list_abbrvs)])

            if temp_batch:
                raise UserError(f'La abreviatura {branch_abbrv} coincide con una secuencia existente.')
            else:
                    
                batch_next = self.env['ir.sequence'].search([('code','=',self.seq_stock_batch)]).number_next_actual or 1
                package_next = self.env['ir.sequence'].search([('code','=',self.seq_stock_package)]).number_next_actual or 1
                sale_next = self.env['ir.sequence'].search([('code','=',self.seq_sale)]).number_next_actual or 1
            
                vals['seq_stock_batch'] = self.env['ir.sequence'].create({
                    'name': f'{branch_name} SECUENCIA PARA AGRUPACIÓN DE ALBARANÉS: {branch_abbrv}',
                    'implementation': 'standard',
                    'code': f'stock.batch.{branch_abbrv}',
                    'active': True,
                    'prefix': f'{branch_abbrv}',
                    'padding': 5,
                    'number_next': batch_next,
                    'number_increment': 1,
                    }).code   

                vals['seq_stock_package'] = self.env['ir.sequence'].create({
                    'name': f'{branch_name} SECUENCIA PARA PAQUETES: {branch_abbrv}',
                    'implementation': 'standard',
                    'code': f'stock.package.{branch_abbrv}',
                    'active': True,
                    'prefix': f'{branch_abbrv}',
                    'padding': 5,
                    'number_next': package_next,
                    'number_increment': 1,
                    }).code   

                vals['seq_sale'] = self.env['ir.sequence'].create({
                    'name': f'{branch_name} SECUENCIA PARA VENTA: {branch_abbrv}',
                    'implementation': 'standard',
                    'code': f'sale.order.{branch_abbrv}',
                    'active': True,
                    'prefix': f'{branch_abbrv}',
                    'padding': 5,
                    'number_next': sale_next,
                    'number_increment': 1,
                    }).code  
            
        return super().write(vals)
 
        
    
    
    
    
class StockBatchExtension(models.Model):
    _inherit = "stock.picking.batch"
    
    def compute_branch(self):
        return self.env.user.branch_id

    current_branch_id = fields.Many2one(string="Rama", comodel_name="res.branch", default=compute_branch, readonly=True, copy=True)
    
    @api.model
    def create(self, vals):
        res = super().create(vals)  
        if res['current_branch_id']:
            res_id = res['current_branch_id'].id
            branch = self.env['res.branch'].browse(res_id).seq_stock_batch
            new_seq_stock = self.env['ir.sequence'].next_by_code(branch)

            stock_name = res['name'] or vals.get('name','')
            
            res['name'] = f'{stock_name}/{new_seq_stock}'

        return res
    
    
    
    
    
    
class StockPackageExtension(models.Model):
    _inherit = "stock.quant.package"
    
    def compute_branch(self):
        return self.env.user.branch_id

    current_branch_id = fields.Many2one(string="Rama", comodel_name="res.branch", default=compute_branch, readonly=True, copy=True)
    
    @api.model
    def create(self, vals):
        res = super().create(vals)  
        if res['current_branch_id']:
            res_id = res['current_branch_id'].id
            branch = self.env['res.branch'].browse(res_id).seq_stock_package
            new_seq_stock = self.env['ir.sequence'].next_by_code(branch)

            stock_name = res['name'] or vals.get('name','')
            
            res['name'] = f'{stock_name}/{new_seq_stock}'

        return res

    
    
      

    
class SaleOrderExtension(models.Model):
    _inherit = "sale.order"

    @api.model
    def create(self, vals):
        res = super().create(vals) 
        if self.env['res.branch'].browse(vals['branch_id']):
            branch = self.env['res.branch'].browse(vals['branch_id']).seq_sale
            new_seq_stock = self.env['ir.sequence'].next_by_code(branch)

            sale_name = res['name'] or vals.get('name','')
            
            res['name'] = f'{sale_name}/{new_seq_stock}'

        return res

    
    