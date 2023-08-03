const sale_module_models = [
    'sale.order',
    'crm.team',
    'product.pricelist',
    'producto.pricelist.item',
    'coupon.program',
    'crm.tag',
];

const purchase_module_models = [
    'purchase.order',
    'product.supplierinfo'
];

const contact_module_models = [
    'res.partner',
    'res.partner.category',
    'res.partner.title',
    'res.partner.industry',
    'res.country',
    'res.country.state',
    'res.country.group',
    'res.bank',
    'res.partner.bank'
];

const accounting_module_models = [
    'account.move',
    'account.payment',
    'hr.expense.sheet',
    'account.move.line',
    'account.transfer.model',
    'account.asset',
    'account.payment.term',
    'account_followup.followup.line',
    'account.incoterms',
    'account.reconcile.model',
    'account.online.link',
    'account.account',
    'account.account.type',
    'account.tax',
    'account.journal',
    'res.currency',
    'account.fiscal.position',
    'account.journal.group',
    'payment.acquirer'
];

const inventary_module_models = [
    'product.template',
    'product.product',
    'delivery.carrier',
    'product.attribute',
    'uom.category',
    'product.category'
];

const view_type = ['form', 'list'];


odoo.define('tsc_restrictions_action_menu.HideAction', function (require) {
    "use strict";

    const BasicModel = require('web.BasicModel');
    const FormController = require('web.FormController');
    const ListController = require('web.ListController');
    var session = require('web.session');


    BasicModel.include({
        _load: function () {
            var self = this;
            var defs = []
            defs.push(this._super(...arguments));

            /**
             * Se define la variable de los grupos para ser usada en el ListController
             */
            /**
             * Sale module
             */
            defs.push(session.user_has_group('tsc_restrictions_action_menu.tsc_see_action_menu_sale_id')
                .then((result) => {
                    if (self.loadParams) {
                        const modelName = self.loadParams.modelName;
                        const viewType = self.loadParams.viewType;
                        if (modelName && sale_module_models.includes(modelName) && viewType && view_type.includes(viewType)) {
                            self.user_is_in_sale_group = result;
                        }
                    }
                }));

            defs.push(session.user_has_group('tsc_restrictions_action_menu.tsc_see_duplicate_sale_id')
                .then((result) => {
                    if (self.loadParams) {
                        const modelName = self.loadParams.modelName;
                        const viewType = self.loadParams.viewType;
                        if (modelName && sale_module_models.includes(modelName) && viewType && view_type.includes(viewType)) {
                            self.user_is_in_duplicate_sale_group = result;
                        }
                    }
                }));

            /**
             * Purchase module
             */

            defs.push(session.user_has_group('tsc_restrictions_action_menu.tsc_see_action_menu_purchase_id')
                .then((result) => {
                    if (self.loadParams) {
                        const modelName = self.loadParams.modelName;
                        const viewType = self.loadParams.viewType;
                        if (modelName && purchase_module_models.includes(modelName) && viewType && view_type.includes(viewType)) {
                            self.user_is_in_purchase_group = result;
                        }
                    }
                }));

            defs.push(session.user_has_group('tsc_restrictions_action_menu.tsc_see_duplicate_purchase_id')
                .then((result) => {
                    if (self.loadParams) {
                        const modelName = self.loadParams.modelName;
                        const viewType = self.loadParams.viewType;
                        if (modelName && purchase_module_models.includes(modelName) && viewType && view_type.includes(viewType)) {
                            self.user_is_in_duplicate_purchase_group = result;
                        }
                    }
                }));

            /**
             * Contact module
             */
            defs.push(session.user_has_group('tsc_restrictions_action_menu.tsc_see_action_contacts_id')
                .then((result) => {
                    if (self.loadParams) {
                        const modelName = self.loadParams.modelName;
                        const viewType = self.loadParams.viewType;
                        if (modelName && contact_module_models.includes(modelName) && viewType && view_type.includes(viewType)) {
                            self.user_is_in_contact_group = result;
                        }
                    }
                }));

            defs.push(session.user_has_group('tsc_restrictions_action_menu.tsc_see_archive_unarchive_contacts_id')
                .then((result) => {
                    if (self.loadParams) {
                        const modelName = self.loadParams.modelName;
                        const viewType = self.loadParams.viewType;
                        if (modelName && contact_module_models.includes(modelName) && viewType && view_type.includes(viewType)) {
                            self.user_is_in_archive_unarchive_contact_group = result;
                        }
                    }
                }));

            /**
             * Accounting Module
             */

            defs.push(session.user_has_group('tsc_restrictions_action_menu.tsc_see_action_accounting_accounting_id')
                .then((result) => {
                    if (self.loadParams) {
                        const modelName = self.loadParams.modelName;
                        const viewType = self.loadParams.viewType;
                        if (modelName && accounting_module_models.includes(modelName) && viewType && view_type.includes(viewType)) {
                            self.user_is_in_accounting_group = result;
                        }
                    }
                }));

            /**
             * Inventory Module
             */

            defs.push(session.user_has_group('tsc_restrictions_action_menu.tsc_see_action_inventory_id')
                .then((result) => {
                    if (self.loadParams) {
                        const modelName = self.loadParams.modelName;
                        const viewType = self.loadParams.viewType;
                        if (modelName && inventary_module_models.includes(modelName) && viewType && view_type.includes(viewType)) {
                            self.user_is_in_inventory_group = result;
                        }
                    }
                }))


            return $.when(...defs);
        }
    })

    FormController.include({
        _getActionMenuItems: function (state) {
            let values = this._super.apply(this, arguments);
            return values;
        }
    });

    ListController.include({
        _getActionMenuItems: function (state) {
            let values = this._super.apply(this, arguments);

            const modelName = this.modelName;
            /**
             * Se agregan las condiciones para ocultar/mostrar la opcion de exportar para la vista list basado en las diferentes combinaciones de grupos
             */
            /**
             * Sale module
             */
            if (modelName && sale_module_models.includes(modelName)) {
                if (!this.model.user_is_in_sale_group && !this.model.user_is_in_duplicate_sale_group) {
                    this.isExportEnable = false;
                }
                if (!this.model.user_is_in_sale_group && this.model.user_is_in_duplicate_sale_group) {
                    this.isExportEnable = false;
                }
            }

            /**
             * Purchase module
             */
            if (modelName && purchase_module_models.includes(modelName)) {
                if (!this.model.user_is_in_purchase_group && !this.model.user_is_in_duplicate_purchase_group) {
                    this.isExportEnable = false;
                }
                if (!this.model.user_is_in_purchase_group && this.model.user_is_in_duplicate_purchase_group) {
                    this.isExportEnable = false;
                }
            }

            /**
             * Contact module
             */
            if (modelName && contact_module_models.includes(modelName)) {
                if (!this.model.user_is_in_contact_group && !this.model.user_is_in_archive_unarchive_contact_group) {
                    this.isExportEnable = false;
                }
                if (!this.model.user_is_in_contact_group && this.model.user_is_in_archive_unarchive_contact_group) {
                    this.isExportEnable = false;
                }
            }

            /**
             * Accounting module
             */
            if (modelName && accounting_module_models.includes(modelName) && !this.model.user_is_in_accounting_group) {
                this.isExportEnable = false;
            }

            /**
             * Inventory module
             */
            if (modelName && inventary_module_models.includes(modelName) && !this.model.user_is_in_inventory_group) {
                this.isExportEnable = false;
            }

            return values;
        }
    });

})

odoo.define('tsc_restrictions_action_menu.BasicView', function (require) {

    "use strict";

    var session = require('web.session');
    var BasicView = require('web.BasicView');

    BasicView.include({

        init: async function (viewInfo, params) {

            var self = this;
            this._super.apply(this, arguments);

            const modelName = self.controllerParams.modelName;
            const viewType = self.controllerParams.viewType;

            /**
             * Se muestra/oculta el menu de Action para la vista form/list de acuerdo a los permisos del usuario
             * Se realiza en el BasicView para no repetir el codigo en el FormController y ListController
             * Se usa el ListController porque la variable isExportEnable no esta disponible en el BasicView sino que es propia del ListController
             */

            /**
             * Sale Module
             */
            const sale_module_include = sale_module_models.includes(modelName);
            const sale_view_type_included = view_type.includes(viewType);

            if (sale_module_include && sale_view_type_included) {

                const user_is_in_sale_group = await session.user_has_group('tsc_restrictions_action_menu.tsc_see_action_menu_sale_id');
                const user_is_in_duplicate_sale_group = await session.user_has_group('tsc_restrictions_action_menu.tsc_see_duplicate_sale_id');

                if (!user_is_in_sale_group && !user_is_in_duplicate_sale_group) {
                    self.controllerParams.toolbarActions.action = [];
                    self.controllerParams.activeActions.duplicate = false;
                    self.controllerParams.activeActions.delete = false;
                    self.controllerParams.archiveEnabled = false;
                }

                if (!user_is_in_sale_group && user_is_in_duplicate_sale_group && modelName != 'sale.order') {
                    self.controllerParams.toolbarActions.action = [];
                    self.controllerParams.activeActions.duplicate = false;
                    self.controllerParams.activeActions.delete = false;
                    self.controllerParams.archiveEnabled = false;
                }

                if (user_is_in_sale_group && !user_is_in_duplicate_sale_group && modelName == 'sale.order') {
                    self.controllerParams.activeActions.duplicate = false;
                }

                if (!user_is_in_sale_group && user_is_in_duplicate_sale_group && modelName == 'sale.order') {
                    self.controllerParams.toolbarActions.action = [];
                    self.controllerParams.activeActions.delete = false;
                }
            }

            /**
             * purchase Module
             */
            const purchase_module_include = purchase_module_models.includes(modelName);
            const purchase_view_type_included = view_type.includes(viewType);

            if (purchase_module_include && purchase_view_type_included) {

                const user_is_in_purchase_group = await session.user_has_group('tsc_restrictions_action_menu.tsc_see_action_menu_purchase_id');
                const user_is_in_duplicate_purchase_group = await session.user_has_group('tsc_restrictions_action_menu.tsc_see_duplicate_purchase_id');

                if (!user_is_in_purchase_group && !user_is_in_duplicate_purchase_group) {
                    self.controllerParams.toolbarActions.action = [];
                    self.controllerParams.activeActions.duplicate = false;
                    self.controllerParams.activeActions.delete = false;
                    self.controllerParams.archiveEnabled = false;
                }

                if (!user_is_in_purchase_group && user_is_in_duplicate_purchase_group && modelName != 'purchase.order') {
                    self.controllerParams.toolbarActions.action = [];
                    self.controllerParams.activeActions.duplicate = false;
                    self.controllerParams.activeActions.delete = false;
                    self.controllerParams.archiveEnabled = false;
                }

                if (user_is_in_purchase_group && !user_is_in_duplicate_purchase_group && modelName == 'purchase.order') {
                    self.controllerParams.activeActions.duplicate = false;
                }

                if (!user_is_in_purchase_group && user_is_in_duplicate_purchase_group && modelName == 'purchase.order') {
                    self.controllerParams.toolbarActions.action = [];
                    self.controllerParams.activeActions.delete = false;
                }
            }

            /**
             * Contact Module
             */
            const contact_module_include = contact_module_models.includes(modelName);
            const contact_view_type_included = view_type.includes(viewType);

            if (contact_module_include && contact_view_type_included) {

                const user_is_in_contact_group = await session.user_has_group('tsc_restrictions_action_menu.tsc_see_action_contacts_id');
                const user_is_in_archive_unarchive_contact_group = await session.user_has_group('tsc_restrictions_action_menu.tsc_see_archive_unarchive_contacts_id');

                if (!user_is_in_contact_group && !user_is_in_archive_unarchive_contact_group) {
                    self.controllerParams.toolbarActions.action = [];
                    self.controllerParams.activeActions.duplicate = false;
                    self.controllerParams.activeActions.delete = false;
                    self.controllerParams.archiveEnabled = false;
                }

                if (!user_is_in_contact_group && user_is_in_archive_unarchive_contact_group && modelName != 'res.partner') {
                    self.controllerParams.toolbarActions.action = [];
                    self.controllerParams.activeActions.duplicate = false;
                    self.controllerParams.activeActions.delete = false;
                    self.controllerParams.archiveEnabled = false;
                }

                if (user_is_in_contact_group && !user_is_in_archive_unarchive_contact_group && modelName == 'res.partner') {
                    self.controllerParams.archiveEnabled = false;
                }

                if (!user_is_in_contact_group && user_is_in_archive_unarchive_contact_group && modelName == 'res.partner') {
                    self.controllerParams.toolbarActions.action = [];
                    self.controllerParams.activeActions.duplicate = false;
                    self.controllerParams.activeActions.delete = false;
                }

            }

            /**
             * Accounting Module
             */
            const accounting_module_include = accounting_module_models.includes(modelName);
            const accounting_view_type_included = view_type.includes(viewType);

            if (accounting_module_include && accounting_view_type_included) {

                const user_is_in_accounting_group = await session.user_has_group('tsc_restrictions_action_menu.tsc_see_action_accounting_accounting_id');

                if (!user_is_in_accounting_group) {
                    self.controllerParams.toolbarActions.action = [];
                    self.controllerParams.activeActions.duplicate = false;
                    self.controllerParams.activeActions.delete = false;
                    self.controllerParams.archiveEnabled = false;
                }
            }

            /**
             * Inventory Module
             */
            const inventory_module_include = inventary_module_models.includes(modelName);
            const inventory_view_type_included = view_type.includes(viewType);

            if (inventory_module_include && inventory_view_type_included) {
                const user_is_in_inventory_group = await session.user_has_group('tsc_restrictions_action_menu.tsc_see_action_inventory_id');

                if (!user_is_in_inventory_group) {
                    self.controllerParams.toolbarActions.action = [];
                    self.controllerParams.activeActions.duplicate = false;
                    self.controllerParams.activeActions.delete = false;
                    self.controllerParams.archiveEnabled = false;
                }

            }
        },

    });

});