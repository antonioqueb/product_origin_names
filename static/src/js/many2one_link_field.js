/** @odoo-module **/
// Widget "som_many2one_link": renderiza un many2one como HIPERVÍNCULO en
// vistas de lista, abriendo la ficha del registro relacionado (proveedor,
// producto, orden de compra) en lugar de la línea. Autocontenido: sin
// dependencias OCA.
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { Component, xml } from "@odoo/owl";

export class SomMany2OneLinkField extends Component {
    static template = xml`
        <a t-if="linkInfo"
           href="#"
           class="o_form_uri fw-normal"
           t-on-click.prevent.stop="openRecord"
           t-esc="linkInfo.name"/>
        <span t-else=""/>
    `;
    static props = { ...standardFieldProps };

    setup() {
        this.actionService = useService("action");
    }

    get linkInfo() {
        const raw = this.props.record.data[this.props.name];
        if (!raw) {
            return null;
        }
        // Forma clásica: [id, display_name]
        if (Array.isArray(raw)) {
            return raw.length ? { id: raw[0], name: raw[1] || "" } : null;
        }
        // Formas nuevas (objeto/DataPoint según versión)
        if (typeof raw === "object") {
            const id = raw.id ?? raw.resId ?? false;
            const name = raw.display_name ?? raw.displayName ?? "";
            return id ? { id, name } : null;
        }
        return null;
    }

    openRecord() {
        const info = this.linkInfo;
        if (!info) {
            return;
        }
        const relation = this.props.record.fields[this.props.name].relation;
        this.actionService.doAction({
            type: "ir.actions.act_window",
            res_model: relation,
            res_id: info.id,
            views: [[false, "form"]],
            target: "current",
        });
    }
}

registry.category("fields").add("som_many2one_link", {
    component: SomMany2OneLinkField,
    displayName: "Many2one como hipervínculo",
    supportedTypes: ["many2one"],
});
