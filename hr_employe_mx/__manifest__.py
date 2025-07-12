{
    'name': "Campos Empleados MX",
    'summary': """
        Módulo para agregar campos personalizados al módulo de Empleados.
    """,
    'description': """
        Este módulo personaliza el modelo de empleados de Odoo 18.
        'Agrega campos personalizados y cálculo automático de vacaciones conforme a la Ley Federal del Trabajo en México.
    """,
    'author': "Drako Tech Solutions",
    'website': "http://mx.drako4ppsdev.com",
    'category': 'Human Resources',
    'version': '1.0',
    # Dependencias: 'hr' es necesario para poder extender el modelo de empleados.
    'depends': ['hr'],
    # Vistas: se carga el archivo XML que contiene las modificaciones de la vista.
    'data': [
        'views/hr_employee_views_custom.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}