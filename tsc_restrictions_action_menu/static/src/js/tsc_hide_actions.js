odoo.define('tsc_restrictions_action_menu.HideAction', function (require) {
    "use strict";

    const BasicModel = require('web.BasicModel');
    const FormController = require('web.FormController');
    const ListController = require('web.ListController');

    BasicModel.include({
        _load: function () {
            var self = this;
            var defs = []
            defs.push(this._super(...arguments));

            /**
             * Se definen las variables de acuerdo a los grupos de usuario para ser usadas en el formController y ListController
             */

            // contacts
            defs.push(this.getSession().user_has_group('tsc_restrictions_action_menu.tsc_see_action_contacts_id').then(
                (result) => {
                    if (self.loadParams) {
                        if (self.loadParams.modelName && self.loadParams.modelName == 'res.partner' && self.loadParams.viewType && (self.loadParams.viewType == 'form' || self.loadParams.viewType == 'list')) {
                            self.hide_action_button_contact = result
                        }
                    }
                }
            ));

            defs.push(this.getSession().user_has_group('tsc_restrictions_action_menu.tsc_see_archive_unarchive_contacts_id').then(
                (result) => {
                    if (self.loadParams) {
                        if (self.loadParams.modelName && self.loadParams.modelName == 'res.partner' && self.loadParams.viewType && (self.loadParams.viewType == 'form' || self.loadParams.viewType == 'list')) {
                            self.hide_action_button_contact_archive_unarchive = result
                        }
                    }
                }
            ));

            // sale
            defs.push(this.getSession().user_has_group('tsc_restrictions_action_menu.tsc_see_action_menu_sale_id').then(
                (result) => {
                    if (self.loadParams) {
                        if (self.loadParams.modelName && self.loadParams.modelName == 'sale.order' && self.loadParams.viewType && (self.loadParams.viewType == 'form' || self.loadParams.viewType == 'list')) {
                            self.hide_action_button_sale = result
                        }
                    }
                }
            ));

            defs.push(this.getSession().user_has_group('tsc_restrictions_action_menu.tsc_see_duplicate_sale_id').then(
                (result) => {
                    if (self.loadParams) {
                        if (self.loadParams.modelName && self.loadParams.modelName == 'sale.order' && self.loadParams.viewType && (self.loadParams.viewType == 'form' || self.loadParams.viewType == 'list')) {
                            self.hide_action_button_duplicate_sale = result
                        }
                    }
                }
            ));

            // purchase
            defs.push(this.getSession().user_has_group('tsc_restrictions_action_menu.tsc_see_action_menu_purchase_id').then(
                (result) => {
                    if (self.loadParams) {
                        if (self.loadParams.modelName && self.loadParams.modelName == 'purchase.order' && self.loadParams.viewType && (self.loadParams.viewType == 'form' || self.loadParams.viewType == 'list')) {
                            self.hide_action_button_purchase = result
                        }
                    }
                }
            ));

            defs.push(this.getSession().user_has_group('tsc_restrictions_action_menu.tsc_see_duplicate_purchase_id').then(
                (result) => {
                    if (self.loadParams) {
                        if (self.loadParams.modelName && self.loadParams.modelName == 'purchase.order' && self.loadParams.viewType && (self.loadParams.viewType == 'form' || self.loadParams.viewType == 'list')) {
                            self.hide_action_button_duplicate_purchase = result
                        }
                    }
                }
            ));

            // accounting
            defs.push(this.getSession().user_has_group('tsc_restrictions_action_menu.tsc_see_action_accounting_accounting_id').then(
                (result) => {
                    if (self.loadParams) {
                        if (self.loadParams.modelName && self.loadParams.modelName == 'account.move' && self.loadParams.viewType && (self.loadParams.viewType == 'form' || self.loadParams.viewType == 'list')) {
                            self.hide_action_button_accounting = result
                        }
                    }
                }
            ));

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

            /**
             * Se condiciona para ocultar/mostrar la opcion de exportar para las diferentes combinaciones de grupos
             */

            if (this.modelName && this.modelName == 'res.partner' && this.viewType && this.viewType == 'list' && !this.model.hide_action_button_contact && this.model.hide_action_button_contact_archive_unarchive) {
                this.isExportEnable = false;
            }


            if (this.modelName && this.modelName == 'sale.order' && this.viewType && this.viewType == 'list') {
                if (!this.model.hide_action_button_sale && this.model.hide_action_button_duplicate_sale) {
                    this.isExportEnable = false;
                }
                if (!this.model.hide_action_button_sale && !this.model.hide_action_button_duplicate_sale) {
                    this.isExportEnable = false;
                }

            }

            if (this.modelName && this.modelName == 'purchase.order' && this.viewType && this.viewType == 'list') {

                if (!this.model.hide_action_button_purchase && this.model.hide_action_button_duplicate_purchase) {
                    this.isExportEnable = false;
                }

                if (!this.model.hide_action_button_purchase && !this.model.hide_action_button_duplicate_purchase) {
                    this.isExportEnable = false;
                }

            }

            if (this.modelName && this.modelName == 'account.move' && this.viewType && this.viewType == 'list' && !this.model.hide_action_button_accounting) {
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

        init: function (viewInfo, params) {

            var self = this;
            this._super.apply(this, arguments);

            var modelName = self.controllerParams.modelName;
            var viewType = self.controllerParams.viewType;

            /**
             * Se muestra/oculta el menu de Action para la vista form/list de acuerdo a los permisos del usuario
             * Se realiza en el BasicView para no repetir el codigo en el FormController y ListController
             * Se usa el ListController porque la variable isExportEnable no esta disponible en el BasicView sino que es propia del ListController
             */

            // contacts
            if (modelName && modelName == 'res.partner' && viewType && (viewType == 'list' || viewType == 'form')) {

                session.user_has_group('tsc_restrictions_action_menu.tsc_see_action_contacts_id')
                    .then(function (is_contact_group) {
                        session.user_has_group('tsc_restrictions_action_menu.tsc_see_archive_unarchive_contacts_id')
                            .then(function (is_archive_unarchive_contact_group) {

                                if (!is_contact_group && !is_archive_unarchive_contact_group) {
                                    self.controllerParams.hasActionMenus = false;
                                }

                                if (is_contact_group && !is_archive_unarchive_contact_group) {
                                    self.controllerParams.archiveEnabled = false;
                                }

                                if (!is_contact_group && is_archive_unarchive_contact_group) {
                                    self.controllerParams.activeActions.delete = false;
                                    self.controllerParams.activeActions.duplicate = false;
                                    self.controllerParams.toolbarActions.action = [];
                                }
                            });
                    });
            }

            // sale
            if (modelName && modelName == 'sale.order' && viewType && (viewType == 'list' || viewType == 'form')) {

                session.user_has_group('tsc_restrictions_action_menu.tsc_see_action_menu_sale_id')
                    .then(function (is_sale_group) {
                        session.user_has_group('tsc_restrictions_action_menu.tsc_see_duplicate_sale_id')
                            .then(function (is_duplicate_sale_group) {

                                if (!is_sale_group && !is_duplicate_sale_group) {
                                    self.controllerParams.toolbarActions.action = [];
                                    self.controllerParams.activeActions.duplicate = false;
                                    self.controllerParams.activeActions.delete = false;
                                }

                                if (is_sale_group && !is_duplicate_sale_group) {
                                    self.controllerParams.activeActions.duplicate = false;
                                }

                                if (!is_sale_group && is_duplicate_sale_group) {
                                    self.controllerParams.activeActions.delete = false;
                                    self.controllerParams.toolbarActions.action = [];
                                }

                            })
                    })
            }

            // purchase
            if (modelName && modelName == 'purchase.order' && viewType && (viewType == 'list' || viewType == 'form')) {

                session.user_has_group('tsc_restrictions_action_menu.tsc_see_action_menu_purchase_id')
                    .then(function (is_purchase_group) {
                        session.user_has_group('tsc_restrictions_action_menu.tsc_see_duplicate_purchase_id')
                            .then(function (is_duplicate_purchase_group) {

                                if (!is_purchase_group && !is_duplicate_purchase_group) {
                                    self.controllerParams.toolbarActions.action = [];
                                    self.controllerParams.activeActions.duplicate = false;
                                    self.controllerParams.activeActions.delete = false;
                                }

                                if (is_purchase_group && !is_duplicate_purchase_group) {
                                    self.controllerParams.activeActions.duplicate = false;
                                }

                                if (!is_purchase_group && is_duplicate_purchase_group) {
                                    self.controllerParams.activeActions.delete = false;
                                    self.controllerParams.toolbarActions.action = [];
                                }

                            })
                    })
            }

            // accounting
            if (modelName && modelName == 'account.move' && viewType && (viewType == 'list' || viewType == 'form')) {
                session.user_has_group('tsc_restrictions_action_menu.tsc_see_action_accounting_accounting_id').
                    then(function (is_accounting_group) {
                        if (!is_accounting_group) {
                            // self.controllerParams.hasActionMenus = false;
                            self.controllerParams.toolbarActions.action = [];
                            self.controllerParams.activeActions.duplicate = false;
                            self.controllerParams.activeActions.delete = false;

                        }
                    })
            }

        },

    });

});