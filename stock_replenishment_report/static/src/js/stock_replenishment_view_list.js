odoo.define(
    'web.StockReplenishmentView',
    ['web.ListView', 'web.view_registry'],
    function (require) {
        "use strict";

        const viewRegistry = require('web.view_registry');
        const ListView = require('web.ListView');

        const StockReplenishmentView = ListView.extend({
            _extractParamsFromAction(action) {
                const params = this._super.apply(this, arguments);
                params.searchMenuTypes = params.searchMenuTypes.filter((menuType) => menuType != "groupBy");
                return params;
            }
        });

        viewRegistry.add('stock_replenishment', StockReplenishmentView);
        return StockReplenishmentView;
    }
);