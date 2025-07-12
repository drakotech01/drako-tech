# Importación de librerías esenciales de Odoo
from odoo import models, fields, api
from datetime import datetime, timedelta
from pytz import timezone

# Extendemos el modelo existente 'hr.attendance' usando herencia.
# Esto nos permite agregar nuevos campos y lógica sin modificar directamente el core.
class HrAttendanceExtended(models.Model):
    _inherit = 'hr.attendance'  # Indicamos que heredamos del modelo original de asistencias.

    # ===========================
    # CAMPOS RELACIONADOS AL EMPLEADO
    # ===========================

    # Campos relacionados para mostrar nombre y datos de empleado en la vista de asistencias.
    # Se obtienen desde el modelo hr.employee (asumiendo que los campos personalizados ya existen ahí).

    name_mx = fields.Char(
        string="Nombre(s)",
        related='employee_id.name_mx',  # Campo de empleado relacionado
        store=True, readonly=True          # Se guarda en base de datos y es solo lectura
    )

    ap_pat_mx = fields.Char(
        string="Apellido Paterno",
        related='employee_id.ap_pat_mx',  # Campo de apellido paterno relacionado
        store=True, readonly=True
    )

    ap_mat_mx = fields.Char(
        string="Apellido Materno",
        related='employee_id.ap_mat_mx',  # Campo de apellido materno relacionado
        store=True, readonly=True
    )

    # Campo combinado de apellidos que concatena paterno y materno.    
    ap_completos = fields.Char(string="Apellidos", compute='_compute_apellidos', store=True)

    @api.depends('ap_pat_mx', 'ap_mat_mx')
    def _compute_apellidos(self):
        """
        Concatena apellido paterno y materno con un espacio.
        """
        for rec in self:
            ap = rec.ap_pat_mx or ''
            am = rec.ap_mat_mx or ''
            rec.ap_completos = f"{ap} {am}".strip()

    # Campo relacionado con el nombre del puesto del empleado
    job_title = fields.Char(
        string="Puesto",
        related='employee_id.job_title',
        store=True, readonly=True
    )

    # Campo relacionado con el nombre del departamento del empleado
    department_id = fields.Many2one(
        string="Departamento",
        related='employee_id.department_id',
        store=True, readonly=True
    )
    
    # Campo relacionado con el nombre de la empresa del empleado
    company_id = fields.Many2one(
        string="Sucursal",
        related='employee_id.company_id',
        store=True, readonly=True
    )


    
    
