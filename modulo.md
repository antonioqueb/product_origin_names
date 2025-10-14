## ./__init__.py
```py
# -*- coding: utf-8 -*-
from . import models
```

## ./__manifest__.py
```py
# -*- coding: utf-8 -*-
{
    'name': 'Nombres de Origen para Productos',
    'version': '18.0.1.0.0',
    'category': 'Inventory/Purchase',
    'summary': 'Gestiona nombres alternativos de productos por proveedor',
    'description': """
        Este módulo permite:
        - Agregar múltiples nombres de origen a productos
        - Mantener orden de prioridad en nombres
        - Reemplazar nombres en reportes de compra
        - Mostrar nombre apropiado en portal de proveedor
    """,
    'author': 'Alphaqueb Consulting',
    'depends': ['product', 'purchase', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_template_views.xml',
        'views/purchase_order_views.xml',
        'reports/purchase_order_report.xml',
        'views/purchase_portal_template.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}```

## ./models/__init__.py
```py
# -*- coding: utf-8 -*-
from . import product_origin_name
from . import product_template
from . import purchase_order_line
```

## ./models/product_origin_name.py
```py
# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ProductOriginName(models.Model):
    _name = 'product.origin.name'
    _description = 'Nombre de Origen del Producto'
    _order = 'sequence, id'

    name = fields.Char(string='Nombre de Origen', required=True)
    sequence = fields.Integer(string='Secuencia', default=10)
    product_tmpl_id = fields.Many2one('product.template', string='Producto', ondelete='cascade', required=True)
    partner_id = fields.Many2one('res.partner', string='Proveedor')
    
    _sql_constraints = [
        ('name_product_unique', 'unique(name, product_tmpl_id)', 'Este nombre de origen ya existe para este producto!')
    ]
```

## ./models/product_template.py
```py
# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    origin_name_ids = fields.One2many(
        'product.origin.name', 
        'product_tmpl_id', 
        string='Nombres de Origen',
        help='Nombres alternativos del producto usados por diferentes proveedores'
    )
    
    @api.model
    def get_primary_origin_name(self):
        """Obtiene el nombre de origen con mayor prioridad"""
        self.ensure_one()
        if self.origin_name_ids:
            return self.origin_name_ids.sorted('sequence')[0].name
        return self.name
```

## ./models/purchase_order_line.py
```py
# -*- coding: utf-8 -*-
from odoo import models, fields, api

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'
    
    display_name_override = fields.Char(
        string='Nombre para Mostrar',
        compute='_compute_display_name_override',
        store=True,
        help='Nombre que se mostrará en reportes y portal'
    )
    
    selected_origin_name_id = fields.Many2one(
        'product.origin.name',
        string='Nombre de Origen Seleccionado',
        help='Permite seleccionar un nombre de origen específico para esta línea'
    )
    
    @api.depends('product_id', 'selected_origin_name_id', 'product_id.product_tmpl_id.origin_name_ids')
    def _compute_display_name_override(self):
        for line in self:
            if line.selected_origin_name_id:
                # Usar el nombre de origen seleccionado manualmente
                line.display_name_override = line.selected_origin_name_id.name
            elif line.product_id and line.product_id.product_tmpl_id.origin_name_ids:
                # Obtener el nombre de origen con mayor prioridad
                primary_origin = line.product_id.product_tmpl_id.origin_name_ids.sorted('sequence')
                if primary_origin:
                    line.display_name_override = primary_origin[0].name
                else:
                    line.display_name_override = line.product_id.name
            else:
                # Usar nombre original del producto
                line.display_name_override = line.product_id.name if line.product_id else ''
    
    @api.onchange('product_id')
    def _onchange_product_id_set_origin_name(self):
        """Al seleccionar un producto, configurar el nombre de origen automáticamente"""
        res = super()._onchange_product_id_set_origin_name() if hasattr(super(), '_onchange_product_id_set_origin_name') else {}
        
        if self.product_id and self.product_id.product_tmpl_id.origin_name_ids:
            # Buscar si hay un nombre de origen para el proveedor actual
            partner_origin = self.product_id.product_tmpl_id.origin_name_ids.filtered(
                lambda x: x.partner_id == self.order_id.partner_id
            )
            if partner_origin:
                self.selected_origin_name_id = partner_origin.sorted('sequence')[0]
            else:
                # Usar el nombre de origen prioritario
                self.selected_origin_name_id = self.product_id.product_tmpl_id.origin_name_ids.sorted('sequence')[0]
        else:
            self.selected_origin_name_id = False
            
        return res
    
    @api.onchange('selected_origin_name_id')
    def _onchange_selected_origin_name_id(self):
        """Recalcular display_name_override cuando cambia el nombre de origen seleccionado"""
        self._compute_display_name_override()
    
    def _prepare_account_move_line(self, move=False):
        """Override para mantener el nombre original en movimientos internos"""
        res = super()._prepare_account_move_line(move=move)
        # En movimientos internos usar siempre el nombre original
        if 'name' in res and self.product_id:
            res['name'] = self.product_id.name
        return res```

## ./reports/purchase_order_report.xml
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Template para el reporte de Orden de Compra -->
    <template id="report_purchaseorder_document_origin" inherit_id="purchase.report_purchaseorder_document">
        <!-- Reemplazar el nombre del producto en las líneas de la orden de compra -->
        <xpath expr="//td[@id='product']/span[@t-field='line.name']" position="replace">
            <span t-out="line.display_name_override or line.name"/>
        </xpath>
    </template>
    
    <!-- Template para el reporte de Solicitud de Cotización -->
    <template id="report_purchasequotation_document_origin" inherit_id="purchase.report_purchasequotation_document">
        <!-- Reemplazar el nombre del producto en las líneas de la cotización -->
        <xpath expr="//td[@id='product']/span[@t-field='order_line.name']" position="replace">
            <span t-out="order_line.display_name_override or order_line.name"/>
        </xpath>
    </template>
</odoo>```

## ./views/product_template_views.xml
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Vista tree para product.origin.name -->
    <record id="view_product_origin_name_tree" model="ir.ui.view">
        <field name="name">product.origin.name.tree</field>
        <field name="model">product.origin.name</field>
        <field name="arch" type="xml">
            <list editable="bottom">
                <field name="sequence" widget="handle"/>
                <field name="name"/>
                <field name="partner_id"/>
            </list>
        </field>
    </record>

    <!-- Vista de producto extendida -->
    <record id="view_product_template_form_origin_names" model="ir.ui.view">
        <field name="name">product.template.form.origin.names</field>
        <field name="model">product.template</field>
        <field name="inherit_id" ref="product.product_template_only_form_view"/>
        <field name="arch" type="xml">
            <xpath expr="//page[@name='purchase']" position="after">
                <page string="Nombres de Origen" name="origin_names">
                    <field name="origin_name_ids" nolabel="1"/>
                </page>
            </xpath>
        </field>
    </record>
</odoo>```

## ./views/purchase_order_views.xml
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="view_purchase_order_form_origin_name" model="ir.ui.view">
        <field name="name">purchase.order.form.origin.name</field>
        <field name="model">purchase.order</field>
        <field name="inherit_id" ref="purchase.purchase_order_form"/>
        <field name="arch" type="xml">
            <!-- Agregar campos en la vista de formulario (cuando se abre una línea) -->
            <xpath expr="//field[@name='order_line']/form//field[@name='product_id']" position="after">
                <field name="selected_origin_name_id" 
                       options="{'no_create': True}" 
                       optional="show"/>
                <field name="display_name_override" invisible="1"/>
            </xpath>
            
            <!-- Agregar campos en la vista de lista (tabla de líneas) -->
            <xpath expr="//field[@name='order_line']/list//field[@name='product_id']" position="after">
                <field name="selected_origin_name_id" 
                       options="{'no_create': True}" 
                       optional="hide"
                       column_invisible="1"/>
                <field name="display_name_override" column_invisible="1"/>
            </xpath>
        </field>
    </record>
</odoo>```

## ./views/purchase_portal_template.xml
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Template para el portal de proveedor - vista web -->
    <template id="portal_my_purchase_order_origin" inherit_id="purchase.portal_my_purchase_order">
        <!-- Reemplazar todas las referencias a line.name en el portal -->
        <xpath expr="//span[@t-field='line.name']" position="replace">
            <span t-out="line.display_name_override or line.name"/>
        </xpath>
    </template>
</odoo>```

