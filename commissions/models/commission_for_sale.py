# -*- coding: utf-8 -*-

from odoo import _, api, exceptions, fields, models


class CommissionForSale(models.Model):
    _name = 'commission.for.sale'
    _description = 'Commission for Sale'

    name = fields.Char(string="Nombre", required=True)
    commission_type = fields.Selection(
        [('fija', 'Fija'), ('basada_en_otra_comision', 'Basada en otra Comisión')],
        string='Tipo de comisión',
        required=True,
        default='fija'
    )

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
    cant_minima_base = fields.Float(string='Can. Mín. Base', required=True)
    bono_base = fields.Float(string='Bono Base', required=True)
    basado_en = fields.Many2one(
        'commission.for.sale',
        string="Basado en",
        domain="[('id', '!=', id),('product_id', '=', product_id or False)]"
    )
    cant_min_base_factor_divisor = fields.Float(
        string='Factor divisor Cant. Mín.',
        default=1.0
    )
    cant_min_base_factor_multiplicador = fields.Float(
        string='Factor multiplicador Cant. Mín.',
        default=1.0
    )
    cant_min_base_factor_extra = fields.Float(string='Factor extra Cant. Mín.')
    cant_min_base_otra_com = fields.Float(
        compute="_compute_cant_min_base_otra_com",
        string='Cant. Mín. Base - otra comisión',
        recursive=True,
        readonly=True,
        store=True
    )
    bono_base_factor_divisor = fields.Float(string='Factor divisor Bono B.', default=1.0)
    bono_base_factor_multiplicador = fields.Float(
        string='Factor multiplicador Bono B.',
        default=1.0
    )
    bono_base_factor_extra = fields.Float(string='Factor extra Bono B.')
    bono_base_otra_com = fields.Float(
        compute="_compute_bono_base_otra_com",
        string='Bono Base - otra comisión',
        recursive=True,
        readonly=True,
        store=True
    )
    forma_de_calculo = fields.Selection(
        [('fijo', 'Fijo'), ('regla_de_tres', 'Regla de tres')],
        default='fijo'
    )

    _sql_constraints = [
        (
            'cant_min_fd_not_zero',
            'CHECK(cant_min_base_factor_divisor != 0)',
            'El factor divisor no puede ser cero. Por favor, verifique'
        ),
        (
            'bono_fd_not_zero',
            'CHECK(bono_base_factor_divisor != 0)',
            'El factor divisor no puede ser cero. Por favor, verifique'
        ),
        (
            'unique_product_id_and_commission_id',
            'UNIQUE(product_id, id)',
            'El producto tiene una o más comisiones repetidas. Por favor, verifique'
        ),
    ]

    @api.constrains('product_id', 'name')
    def _check_unique_product_id_and_insensitive_commission_name(self):
        for record in self:
            if record.product_id and record.name and self.search_count([
                ('product_id', '=', record.product_id.id),
                ('name', 'ilike', record.name),
                ('id', '!=', record.id)
            ]) > 0:
                raise exceptions.ValidationError(
                    _('El producto tiene una o más comisiones con nombres repetidos. Por favor, verifique')
                )

    @api.onchange('name', 'product_id')
    def _onchange_product_id(self):
        for record in self:
            if record.name:
                if record.product_id and record.product_id._origin:
                    record['product_id'] = record.product_id._origin
            else:
                record.update({'product_id': False, 'categ_id': False})
                break

    @api.depends(
        "commission_type",
        "cant_min_base_factor_divisor",
        "cant_min_base_factor_multiplicador",
        "cant_min_base_factor_extra",
        "basado_en",
        "basado_en.cant_minima_base",
        "basado_en.commission_type",
        "basado_en.cant_min_base_otra_com",
    )
    def _compute_cant_min_base_otra_com(self):
        for commission in self:
            if commission.commission_type == 'basada_en_otra_comision' and commission.cant_min_base_factor_divisor > 0:
                cant_min = (
                    commission.basado_en.cant_minima_base
                    if commission.basado_en.commission_type == 'fija'
                    else commission.basado_en.cant_min_base_otra_com
                )
                commission.cant_min_base_otra_com = (
                    (cant_min / commission.cant_min_base_factor_divisor) *
                    commission.cant_min_base_factor_multiplicador
                ) + commission.cant_min_base_factor_extra

    @api.depends(
        "commission_type",
        "bono_base_factor_divisor",
        "bono_base_factor_multiplicador",
        "bono_base_factor_extra",
        "basado_en",
        "basado_en.bono_base",
        "basado_en.commission_type",
        "basado_en.bono_base_otra_com",
    )
    def _compute_bono_base_otra_com(self):
        for commission in self:
            if commission.commission_type == 'basada_en_otra_comision' and commission.bono_base_factor_divisor > 0:
                bono = (
                    commission.basado_en.bono_base
                    if commission.basado_en.commission_type == 'fija'
                    else commission.basado_en.bono_base_otra_com
                )
                commission.bono_base_otra_com = (
                    (bono / commission.bono_base_factor_divisor) *
                    commission.bono_base_factor_multiplicador
                ) + commission.bono_base_factor_extra


class ConfigurationCollection(models.Model):
    _name = "configuration.collection"
    _description = "Configuración del porcentaje a pagar por las cobranzas realizadas"

    name = fields.Char(string="Nombre", default=" ")
    percentage = fields.Float(string="Porcentaje (%) de comisión", required=True)
    account_ids = fields.Many2many(
        'account.account',
        'collection_id',
        string="Cuentas contables a considerar",
        required=True,
        domain="[('user_type_id', '=', '%(account.data_account_type_liquidity)d')]",
    )

    _sql_constraints = [
        (
            'percentage_not_negative',
            'CHECK(percentage < 0)',
            'El porcentaje no puede ser un número negativo. Por favor, verifique'
        ),
    ]

    @api.model
    def create(self, vals):
        res = super(ConfigurationCollection, self).create(vals)

        configs = self.search(["id", "!=", res.id])
        account_ids = configs.account_ids
        configs.unlink()
        account_ids.collection_id = res.id

        return res

    def write(self, values):
        res = super(ConfigurationCollection, self).write(values)

        self.env['account.account'].search([
            ('user_type_id', '=', self.env.ref("account.data_account_type_liquidity").id),
            ('collection_id', '=', self.id)
        ]).collection_id = False

        self.account_ids.collection_id = self.id

        return res
