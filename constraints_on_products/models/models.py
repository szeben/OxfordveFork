# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = "product.template"
    """
        Modelo heredado para aplicar ciertas restricciones al Crear/Actualizar un producto,
        de acuerdo al grupo en el que sea miembro el usuario logeado.
    """

    @api.model_create_multi
    def create(self, vals_list):
        ''' Store the initial standard price in order to be able to retrieve the cost of a product template for a given date'''
        for vals in vals_list:
            self._sanitize_vals(vals)


        if 'sale_ok' in vals_list[0] or 'purchase_ok' in vals_list[0] or 'can_be_expensed' in vals_list[0]:
            if vals_list[0].get('sale_ok') == True and not self.env.user.has_group('constraints_on_products.group_inventory_check_sale_ok'):
                raise UserError(_('No tiene permitido crear o modificar un producto con el campo "Puede ser vendido" verificado.'
                                'Por favor comuníquese con su supervisor.'))
            if vals_list[0].get('purchase_ok') == True and not self.env.user.has_group('constraints_on_products.group_inventory_check_purchase_ok'):
                raise UserError(_('No tiene permitido crear o modificar un producto con el campo "Puede ser comprado" verificado.'
                                'Por favor comuníquese con su supervisor.'))
            if vals_list[0].get('can_be_expensed') == True and not self.env.user.has_group('constraints_on_products.group_inventory_check_can_be_expensed'):
                raise UserError(_('No tiene permitido crear o modificar un producto con el campo "Puede ser un gasto" verificado.'
                                'Por favor comuníquese con su supervisor.'))
            

        templates = super(ProductTemplate, self).create(vals_list)
        if "create_product_product" not in self._context:
            templates._create_variant_ids()

        # This is needed to set given values to first variant after creation
        for template, vals in zip(templates, vals_list):
            related_vals = {}
            if vals.get('barcode'):
                related_vals['barcode'] = vals['barcode']
            if vals.get('default_code'):
                related_vals['default_code'] = vals['default_code']
            if vals.get('standard_price'):
                related_vals['standard_price'] = vals['standard_price']
            if vals.get('volume'):
                related_vals['volume'] = vals['volume']
            if vals.get('weight'):
                related_vals['weight'] = vals['weight']
            # Please do forward port
            if vals.get('packaging_ids'):
                related_vals['packaging_ids'] = vals['packaging_ids']
            if related_vals:
                template.write(related_vals)

        return templates

    def write(self, vals):
        self._sanitize_vals(vals)
        if 'uom_id' in vals or 'uom_po_id' in vals:
            uom_id = self.env['uom.uom'].browse(vals.get('uom_id')) or self.uom_id
            uom_po_id = self.env['uom.uom'].browse(vals.get('uom_po_id')) or self.uom_po_id
            if uom_id and uom_po_id and uom_id.category_id != uom_po_id.category_id:
                vals['uom_po_id'] = uom_id.id

                
        if 'sale_ok' in vals or 'purchase_ok' in vals or 'can_be_expensed' in vals:
            if vals.get('sale_ok') == True and not self.env.user.has_group('constraints_on_products.group_inventory_check_sale_ok'):
                raise UserError(_('No tiene permitido crear o modificar un producto con el campo "Puede ser vendido" verificado.'
                                'Por favor comuníquese con su supervisor.'))
            if vals.get('purchase_ok') == True and not self.env.user.has_group('constraints_on_products.group_inventory_check_purchase_ok'):
                raise UserError(_('No tiene permitido crear o modificar un producto con el campo "Puede ser comprado" verificado.'
                                'Por favor comuníquese con su supervisor.'))
            if vals.get('can_be_expensed') == True and not self.env.user.has_group('constraints_on_products.group_inventory_check_can_be_expensed'):
                raise UserError(_('No tiene permitido crear o modificar un producto con el campo "Puede ser un gasto" verificado.'
                                'Por favor comuníquese con su supervisor.'))


        res = super(ProductTemplate, self).write(vals)
        if 'attribute_line_ids' in vals or (vals.get('active') and len(self.product_variant_ids) == 0):
            self._create_variant_ids()
        if 'active' in vals and not vals.get('active'):
            self.with_context(active_test=False).mapped('product_variant_ids').write({'active': vals.get('active')})
        if 'image_1920' in vals:
            self.env['product.product'].invalidate_cache(fnames=[
                'image_1920',
                'image_1024',
                'image_512',
                'image_256',
                'image_128',
                'can_image_1024_be_zoomed',
            ])
            # Touch all products that will fall back on the template field
            # This is done because __last_update is used to compute the 'unique' SHA in image URLs
            # for making sure that images are not retrieved from the browser cache after a change
            # Performance discussion outcome:
            # Actually touch all variants to avoid using filtered on the image_variant_1920 field
            self.product_variant_ids.write({})
        return res


# class ProductProduct(models.Model):
#     _inherit = "product.product"

#     @api.model_create_multi
#     def create(self, vals_list):
#         for vals in vals_list:
#             self.product_tmpl_id._sanitize_vals(vals)
#         print('before products assign', self, vals_list)
#         products = super(ProductProduct, self.with_context(create_product_product=True)).create(vals_list)
#         print('products value', products)
#         # `_get_variant_id_for_combination` depends on existing variants
#         self.clear_caches()
#         return products

#     def write(self, values):
#         self.product_tmpl_id._sanitize_vals(values)
#         print('before res assign in product.product', self, values)
#         res = super(ProductProduct, self).write(values)
#         print('res value in product.product', res)
#         if 'product_template_attribute_value_ids' in values:
#             # `_get_variant_id_for_combination` depends on `product_template_attribute_value_ids`
#             self.clear_caches()
#         elif 'active' in values:
#             # `_get_first_possible_variant_id` depends on variants active state
#             self.clear_caches()
#         return res

