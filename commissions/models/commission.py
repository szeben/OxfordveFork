# -*- coding: utf-8 -*-

from odoo import _, api, exceptions, fields, models


class CommissionCommission(models.AbstractModel):
    _name = 'commission.commission'
    _description = 'Commissions'

    name = fields.Char(string="Nombre", required=True)
    commission_type = fields.Selection(
        [('fija', 'Fija'), ('basada_en_otra_comision', 'Basada en otra Comisión')],
        string='Tipo de comisión',
        required=True,
        default='fija'
    )

    cant_minima_base = fields.Float(string='Can. Mín. Base', required=True)
    bono_base = fields.Float(string='Bono Base', required=True)
    basado_en = fields.Many2one(
        comodel_name='commission.commission',
        string="Basado en",
        domain="[('id', '!=', id)]"
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
        store=True
    )
    forma_de_calculo = fields.Selection(
        [('fijo', 'Fijo'), ('regla_de_tres', 'Regla de tres')],
        string='Forma de cálculo',
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
    ]

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

    def compute_commission(self, total_sales_amount=0.0):
        self.ensure_one()
        amount = 0.0

        if self.commission_type == 'fija':
            if self.forma_de_calculo == 'fijo':
                amount = self.bono_base
            else:
                amount = total_sales_amount * self.bono_base / self.cant_minima_base
        elif self.commission_type == 'basada_en_otra_comision':
            if self.forma_de_calculo == 'fijo':
                amount = self.bono_base_otra_com
            else:
                amount = total_sales_amount * self.bono_base_otra_com / self.cant_min_base_otra_com

        return amount


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
            'percentage_not_zero',
            'CHECK(percentage >= 0)',
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
