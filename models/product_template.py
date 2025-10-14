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
