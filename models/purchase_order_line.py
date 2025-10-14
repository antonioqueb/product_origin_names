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
        return res