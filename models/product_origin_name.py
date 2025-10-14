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
