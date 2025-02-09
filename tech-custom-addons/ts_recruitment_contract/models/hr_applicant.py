from odoo import models
# from odoo.exceptions import ValidationError

class HRApplicant(models.Model):
    _inherit = "hr.applicant"


    def create_contract_from_applicant(self):
        for rec in self:
            type_id = int(self.env['ir.config_parameter'].sudo().get_param('ts_recruitment_contract.type_id', default=False))
            structure_type_id = int(self.env['ir.config_parameter'].sudo().get_param('ts_recruitment_contract.structure_type_id', default=False))
            contract_type_id = int(self.env['ir.config_parameter'].sudo().get_param('ts_recruitment_contract.contract_type_id', default=False))
            resource_calendar_id = int(self.env['ir.config_parameter'].sudo().get_param('ts_recruitment_contract.resource_calendar_id', default=False))
            analytic_account_id = int(self.env['ir.config_parameter'].sudo().get_param('ts_recruitment_contract.analytic_account_id', default=False))
            journal_id = int(self.env['ir.config_parameter'].sudo().get_param('ts_recruitment_contract.journal_id', default=False))
            context = {
                'default_employee_id': rec.emp_id.id,
                'default_date_start': rec.availability,###
                'default_hr_responsible_id': rec.user_id.id,
                'default_wage': rec.salary_proposed,
                'default_type_id': type_id,
                'default_struct_id': structure_type_id,
                'default_contract_type_id': contract_type_id,
                'default_resource_calendar_id': resource_calendar_id,
                'default_analytic_account_id': analytic_account_id,
                'default_journal_id': journal_id,
                'default_department_id': rec.department_id.id,
            }
            return {
                'name': "Create Contract",
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'hr.contract',
                'target': 'current',
                'context': context,
            }