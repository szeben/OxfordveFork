/** @odoo-module **/

import { registry } from "@web/core/registry";
import { PivotModel } from "@web/views/pivot/pivot_model";
import { PivotView } from "@web/views/pivot/pivot_view";
const viewRegistry = registry.category("views");


class AssignedCommissionsPivotModel extends PivotModel {
    _getTableRows(tree, columns) {
        const tableRows = super._getTableRows(...arguments);
        if (!tree.sortedKeys) {
            // if (tree.directSubTrees.size > 0 && tree.root.labels.length === 0) {
            //     console.log(tree, tableRows);
            // }
            tableRows.sort(function (a, b) {
                if (a.isLeaf && b.isLeaf) {
                    if (a.title > b.title) {
                        return 1;
                    }
                    else if (a.title < b.title) {
                        return -1;
                    }
                }
                return 0;
            });
        };
        return tableRows;
    }
}

export class AssignedCommissionsPivotView extends PivotView { }

AssignedCommissionsPivotView.Model = AssignedCommissionsPivotModel;

viewRegistry.add("assigned_commissions_pivot_view", AssignedCommissionsPivotView);