# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class HrApplicant(models.Model):
    _inherit = 'hr.applicant'

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
        if vals.get('full_name_mx'):
            vals['name'] = vals['full_name_mx']  # Se usa como nombre principal del candidato
        return super(HrApplicant, self).create(vals)

    # Método para avanzar a la siguiente etapa
    def action_advance_stage(self):
        for applicant in self:
            current_stage = applicant.stage_id
            next_stage = self.env['hr.recruitment.stage'].search([
                ('job_id', '=', applicant.job_id.id),
                ('sequence', '>', current_stage.sequence)
            ], order='sequence asc', limit=1)

            if not next_stage:
                raise UserError(_("No hay una siguiente etapa configurada para este puesto."))

            # Actualiza el estado a "in_progress" (interno)
            applicant.write({
                'stage_id': next_stage.id,
                'state'   : 'in_progress'
            })

    # Método para rechazar el candidato (etapa final de rechazo)
    def action_reject_applicant(self):
        for applicant in self:
            reject_stage = self.env['hr.recruitment.stage'].search([
                ('job_id', '=', applicant.job_id.id),
                ('name', 'ilike', 'rechazado')  # Puede ser "Rechazado" u otro similar
            ], limit=1)

            if not reject_stage:
                raise UserError(_("No hay una etapa de rechazo configurada."))

            applicant.write({
                'stage_id': reject_stage.id,
                'state': 'cancel'
            })

    # Evitar retroceso de etapa manual
    @api.onchange('stage_id')
    def _onchange_stage_id(self):
        if self.stage_id and self.stage_id.sequence < self._origin.stage_id.sequence:
            raise UserError(_("No puedes regresar a una etapa anterior."))

    
    def action_create_employee_custom(self):
        """Crea un empleado desde el candidato y redirige a su formulario."""

        for applicant in self:
            if applicant.employee_id:
                raise UserError(_("Este candidato ya tiene un empleado vinculado."))

            # Construir el nombre completo personalizado
            nombre = applicant.name_mx or ''
            paterno = applicant.ap_pat_mx or ''
            materno = applicant.ap_mat_mx or ''
            full_name = f"{nombre} {paterno} {materno}".strip() or "Empleado"

            # Preparar los datos del nuevo empleado
            employee_vals = {
                'name': full_name,
                'name_mx': applicant.name_mx,
                'ap_pat_mx': applicant.ap_pat_mx,
                'ap_mat_mx': applicant.ap_mat_mx,
                'job_title': applicant.job_id.name if applicant.job_id else '',
                'department_id': applicant.department_id.id if applicant.department_id else False,
                'work_email': applicant.email_from,
                'work_phone': applicant.partner_phone,
                'birth_date': getattr(applicant, 'birth_date', False),
                'rfc': getattr(applicant, 'rfc', ''),
                'curp': getattr(applicant, 'curp', ''),
                'image_1920': False,  # evita el avatar
            }

            # Crear el empleado
            employee = self.env['hr.employee'].sudo().with_context(skip_avatar=True).create(employee_vals)

            # Enlazar el empleado al applicant
            applicant.employee_id = employee.id

            # Devolver acción para redirigir al formulario del nuevo empleado
            return {
                'type': 'ir.actions.act_window',
                'name': _('Empleado'),
                'view_mode': 'form',
                'res_model': 'hr.employee',
                'res_id': employee.id,
                'target': 'current',
            }
    
    @api.model
    def create(self, vals):
        record = super().create(vals)
        if record.stage_id:
            record._log_stage_history(record.stage_id.id)
        return record

    def write(self, vals):
        res = super().write(vals)
        for record in self:
            if 'stage_id' in vals:
                record._log_stage_history(vals['stage_id'])
        return res

    def _log_stage_history(self, stage_id):
        # Evita duplicados si ya existe registro para esta etapa
        last_stage = self.env['hr.applicant.stage.history'].search([
            ('applicant_id', '=', self.id),
            ('stage_id', '=', stage_id)
        ], limit=1)
        if not last_stage:
            self.env['hr.applicant.stage.history'].create({
                'applicant_id': self.id,
                'stage_id': stage_id,
            })

        
    # Campo para registrar el historial de etapas
    stage_history_ids = fields.One2many(
        'hr.applicant.stage.history', 'applicant_id', string='Historial de Etapas', readonly=True
    )

    stage_change_date = fields.Datetime(string='Último cambio de etapa', readonly=True)

    @api.model
    def create(self, vals):
        # Al crear, registrar la etapa inicial
        applicant = super().create(vals)
        applicant._log_stage_history(applicant.stage_id)
        return applicant

    def write(self, vals):
        # Si cambia de etapa, registrar el historial
        if 'stage_id' in vals:
            for applicant in self:
                applicant._log_stage_duration()
        return super().write(vals)

    def _log_stage_duration(self):
        """Registra el tiempo en la etapa anterior antes de cambiar"""
        for rec in self:
            if rec.stage_change_date:
                now = fields.Datetime.now()
                duration = (now - rec.stage_change_date).days
                self.env['hr.applicant.stage.history'].create({
                    'applicant_id': rec.id,
                    'stage_id': rec.stage_id.id,
                    'change_date': now,
                    'days_in_stage': duration,
                })
            rec.stage_change_date = fields.Datetime.now()

    def _log_stage_history(self, stage):
        """Inicializa el historial al crear"""
        self.env['hr.applicant.stage.history'].create({
            'applicant_id': self.id,
            'stage_id': stage.id,
            'change_date': fields.Datetime.now(),
            'days_in_stage': 0,
        })
        self.stage_change_date = fields.Datetime.now()

    def action_advance_stage(self):
        for applicant in self:
            current_stage = applicant.stage_id
            now = fields.Datetime.now()

            # Buscar el último cambio registrado
            last_history = self.env['hr.applicant.stage.history'].search(
                [('applicant_id', '=', applicant.id)],
                order='change_date desc',
                limit=1
            )

            # Calcular días desde el último cambio
            if last_history:
                delta = now - last_history.change_date
                days = delta.days
            else:
                days = 0

            # Guardar el historial actual
            self.env['hr.applicant.stage.history'].create({
                'applicant_id': applicant.id,
                'stage_id': current_stage.id,
                'change_date': now,
                'days_in_stage': days,
            })

            # Buscar siguiente etapa (misma lógica anterior)
            stages = self.env['hr.recruitment.stage'].search([], order='sequence')
            current_index = stages.ids.index(current_stage.id)
            if current_index + 1 < len(stages):
                next_stage = stages[current_index + 1]
                applicant.write({
                    'stage_id': next_stage.id,
                    'stage_state': 'in_progress',
                })

    def action_reject_applicant(self):
        """Marca al candidato como rechazado"""
        for applicant in self:
            rejected_stage = self.env['hr.recruitment.stage'].search(
                [('name', 'ilike', 'rechazado')], limit=1
            )
            if rejected_stage:
                applicant.write({
                    'stage_id': rejected_stage.id,
                    'stage_state': 'blocked',
                })
            else:
                raise UserError("No se encontró una etapa de rechazo definida.")

