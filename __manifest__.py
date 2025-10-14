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
}