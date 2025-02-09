import logging
from odoo import fields,models, _

_logger = logging.getLogger(__name__)



class HrLeaveType(models.Model):
    _inherit = 'hr.leave.type'

    duration_of_timesheet = fields.Integer(string="Duration of Timesheet")


class Holidays(models.Model):
    _inherit = "hr.leave"


    def _timesheet_prepare_line_values(self, index, work_hours_data, day_date, work_hours_count):
        self.ensure_one()

        off_working_hours = self.holiday_status_id.duration_of_timesheet or 0.0

        return {
            'name': _("Time Off (%s/%s)" % (index + 1, len(work_hours_data))),
            'project_id': self.holiday_status_id.timesheet_project_id.id,
            'task_id': self.holiday_status_id.timesheet_task_id.id,
            'account_id': self.holiday_status_id.timesheet_project_id.analytic_account_id.id,
            'unit_amount': off_working_hours,
            'user_id': self.employee_id.user_id.id,
            'date': day_date,
            'holiday_id': self.id,
            'employee_id': self.employee_id.id,
            'company_id': self.holiday_status_id.timesheet_task_id.company_id.id or self.holiday_status_id.timesheet_project_id.company_id.id,
        }
