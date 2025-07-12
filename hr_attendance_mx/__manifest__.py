# -*- coding: utf-8 -*-
{
    'name': 'HR Attendance MX',
    'version': '1.0',
    'summary': 'Extiende asistencias con datos de empleados personalizados',
    'author': "Drako Tech Solutions",
    'website': "http://mx.drako4ppsdev.com",
    'category': 'Human Resources',
    'depends': ['hr_attendance', 'hr_employe_mx', 'hr'],
    'data': [
        'views/hr_attendance_custom_views.xml',  # Vistas personalizadas para asistencias
    ],
    'installable': True,
    'application': False,
}