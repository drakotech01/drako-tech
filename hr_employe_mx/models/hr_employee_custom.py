from odoo import models, fields, api
from datetime import date

# Se hereda el modelo 'hr.employee' para agregarle nuevos campos.
class HrEmployeeCustom(models.Model):
    _inherit = 'hr.employee'

    # Campos extendidos del empleado
    name_mx = fields.Char(string='Nombre(s)', required=True)
    ap_pat_mx = fields.Char(string='Apellido Paterno', required=True)
    ap_mat_mx = fields.Char(string='Apellido Materno')
    full_name_mx = fields.Char(string='Nombre Completo MX', compute='_compute_full_name', store=True)

    # Dirección extendida
    st_name_mx = fields.Char(string='Calle', required=True)
    st_num_mx = fields.Char(string='Número Exterior', required=True)
    st_num_int_mx = fields.Char(string='Número Interior')
    st_colony_mx = fields.Char(string='Colonia', required=True)
    address_mx = fields.Char(string='Dirección Principal', compute='_compute_full_address', store=True)

    # Fecha de ingreso (usa contract_date)
    fecha_ingreso = fields.Date(string='Fecha de Ingreso', compute='_compute_fecha_ingreso', store=True)
    antiguedad_mx = fields.Integer(string='Años de Antigüedad', compute='_compute_antiguedad', store=True)
    dias_vacaciones_mx = fields.Integer(string='Días de Vacaciones', compute='_compute_dias_vacaciones', store=True)

    # Nivel de Estudios
    level_edu_mx = fields.Selection([
        ('primaria', 'Primaria'),
        ('secundaria', 'Secundaria'),
        ('preparatoria', 'Preparatoria'),
        ('tecnico', 'Técnico'),
        ('licenciatura', 'Licenciatura'),
        ('maestria', 'Maestría'),
        ('doctorado', 'Doctorado'),
        ('otro', 'Otro'),
    ], string='Nivel de Estudios', store=True)

    # Estado de Estudios
    lvl_edu_mx = fields.Selection([
        ('titulo', 'Titulado'),
        ('egresado', 'Egresado'),
        ('cursando', 'Cursando'),
        ('trunca', 'Trunca'),
        ('pasante', 'Pasante'),        
    ], string='Estado de Estudios', store=True )
    
    @api.model
    def create(self, vals):
        nombre = vals.get('name_mx', '')
        ap_pat = vals.get('ap_pat_mx', '')
        ap_mat = vals.get('ap_mat_mx', '')
        partes = list(filter(None, [nombre, ap_pat, ap_mat]))
        vals['name'] = ' '.join(partes)
        return super(HrEmployeeCustom, self).create(vals)

    def write(self, vals):
        for rec in self:
            nombre = vals.get('name_mx', rec.name_mx)
            ap_pat = vals.get('ap_pat_mx', rec.ap_pat_mx)
            ap_mat = vals.get('ap_mat_mx', rec.ap_mat_mx)
            partes = list(filter(None, [nombre, ap_pat, ap_mat]))
            vals['name'] = ' '.join(partes)
        return super(HrEmployeeCustom, self).write(vals)

    @api.depends('name_mx', 'ap_pat_mx', 'ap_mat_mx')
    def _compute_full_name_mx(self):
        for rec in self:
            partes = filter(None, [rec.name_mx, rec.ap_pat_mx, rec.ap_mat_mx])
            full_name = ' '.join(partes)
            rec.full_name_mx = full_name
            rec.name = full_name  # Actualiza el campo 'name' del modelo base

    @api.depends('st_name_mx', 'st_num_mx', 'st_num_int_mx')
    def _compute_full_address(self):
        for rec in self:
            interior = f" Int. {rec.st_num_int_mx}" if rec.st_num_int_mx else ""
            rec.address_mx = f"{rec.st_name_mx or ''} {rec.st_num_mx or ''}{interior}".strip()
            
            rec.private_street = rec.address_mx  # Actualiza el campo 'private_street' del modelo base



    @api.depends('contract_id.date_start')
    def _compute_fecha_ingreso(self):
        for rec in self:
            rec.fecha_ingreso = rec.contract_id.date_start if rec.contract_id and rec.contract_id.date_start else False

    @api.depends('fecha_ingreso')
    def _compute_antiguedad(self):
        for rec in self:
            if rec.fecha_ingreso:
                today = date.today()
                rec.antiguedad_mx = today.year - rec.fecha_ingreso.year - ((today.month, today.day) < (rec.fecha_ingreso.month, rec.fecha_ingreso.day))
            else:
                rec.antiguedad_mx = 0    

    @api.depends('antiguedad_mx')
    def _compute_dias_vacaciones(self):
        for rec in self:
            años = rec.antiguedad_mx
            if años <= 0:
                rec.dias_vacaciones_mx = 0
            elif años == 1:
                rec.dias_vacaciones_mx = 12
            elif años == 2:
                rec.dias_vacaciones_mx = 14
            elif años == 3:
                rec.dias_vacaciones_mx = 16
            elif años == 4:
                rec.dias_vacaciones_mx = 18
            elif años == 5:
                rec.dias_vacaciones_mx = 20
            elif años >= 6:
                extra = ((años - 6) // 5 + 1) * 2
                rec.dias_vacaciones_mx = 20 + extra
    