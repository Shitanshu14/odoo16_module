from odoo import models, fields, api


class Department(models.Model):
    _inherit = 'hr.department'

    employee_ids = fields.One2many('hr.employee', 'department_id', string='Employees')
    department_expense = fields.Float(string="Department Expense", compute='_compute_department_expense',
                                          store=True)

    @api.depends('employee_ids.contract_ids.wage', 'employee_ids.contract_ids.state')
    def _compute_department_expense(self):
        for department in self:
            # Get active employees
            active_employees = department.employee_ids.filtered(lambda e: e.active)
            # Initialize total_salary
            total_salary = 0
            # Sum the wages from active contracts
            for employee in active_employees:
                # Get the wages of the employee's open contracts
                wages = employee.contract_ids.filtered(lambda c: c.state == 'open').mapped('wage')
                total_salary += sum(wages)  # Sum the individual wages
            department.department_expense = total_salary
