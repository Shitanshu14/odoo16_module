from odoo import fields, models, api

class AccountFiscalYear(models.Model):
    _inherit = 'account.fiscal.year'
    _description = 'Fiscal Year'

    fiscal_year_id = fields.Many2one('account.fiscal.year', string="Fiscal Year")

    @api.model
    def create(self, vals):
        fiscal_year = super(AccountFiscalYear, self).create(vals)
        self._create_dynamic_filter(fiscal_year)
        return fiscal_year

    def write(self, vals):
        # Call the super method to ensure the write operation is processed
        result = super(AccountFiscalYear, self).write(vals)
        # If the name of the fiscal year is updated, update the filters
        if 'name' in vals:
            for fiscal_year in self:
                self._update_dynamic_filter_name(fiscal_year)
        self.create_filters_for_existing_fiscal_years()
        return result

    def _create_dynamic_filter(self, fiscal_year):
        models_to_filter = [
            {'model': 'account.move', 'domain': [
                '&',
                ('date', '>=', fiscal_year.date_from),
                ('date', '<=', fiscal_year.date_to),
                ('company_id', '=', fiscal_year.company_id.id)
            ]},
            {'model': 'account.bank.statement.line', 'domain': [
                '&',
                ('date', '>=', fiscal_year.date_from),
                ('date', '<=', fiscal_year.date_to),
                ('company_id', '=', fiscal_year.company_id.id)
            ]},
            {'model': 'account.bank.statement', 'domain': [
                '&',
                ('date', '>=', fiscal_year.date_from),
                ('date', '<=', fiscal_year.date_to),
                ('company_id', '=', fiscal_year.company_id.id)
            ]},
            {'model': 'account.payment', 'domain': [
                '&',
                ('payment_date', '>=', fiscal_year.date_from),
                ('payment_date', '<=', fiscal_year.date_to),
                ('company_id', '=', fiscal_year.company_id.id)
            ]},
            {'model': 'hr.expense.sheet', 'domain': [
                '&',
                ('date_from', '>=', fiscal_year.date_from),
                ('date_to', '<=', fiscal_year.date_to),
                ('company_id', '=', fiscal_year.company_id.id)
            ]},
        ]

        for model in models_to_filter:
            filter_vals = {
                'name': f"{fiscal_year.name}",
                'model_id': model['model'],
                'domain': model['domain'],
                'context': {},
                'is_default': False,
                'user_id': False,
                'sort': 'date desc',
                'fiscal_year_id': fiscal_year.id,  # Set the fiscal_year_id field
            }
            self.env['ir.filters'].create(filter_vals)

    def _update_dynamic_filter_name(self, fiscal_year):
        # Fetch filters related to the fiscal year
        filters = self.env['ir.filters'].search([
            ('fiscal_year_id', '=', fiscal_year.id),
        ])

        # Update the names of the filters
        for filter_record in filters:
            filter_record.name = f"{fiscal_year.name}"


    def create_filters_for_existing_fiscal_years(self, **kwargs):
        existing_fiscal_years = self.search([])

        for fiscal_year in existing_fiscal_years:
            existing_filters = self.env['ir.filters'].search([('fiscal_year_id', '=', fiscal_year.id)])

            if not existing_filters:
                self._create_dynamic_filter(fiscal_year)

class IrFilters(models.Model):
    _inherit = 'ir.filters'

    fiscal_year_id = fields.Many2one('account.fiscal.year', string="Fiscal Year")



class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'

    @api.model
    def create(self, vals):
        task_type = super(ProjectTaskType, self).create(vals)
        self._create_or_update_dynamic_filters(task_type)
        return task_type

    def write(self, vals):
        old_values = {}
        for task_type in self:
            old_values[task_type.id] = {
                'legend_blocked': task_type.legend_blocked,
                'legend_normal': task_type.legend_normal,
                'legend_done': task_type.legend_done,
            }
        result = super(ProjectTaskType, self).write(vals)
        if any(field in vals for field in ['legend_blocked', 'legend_normal', 'legend_done']):
            for task_type in self:
                self._create_or_update_dynamic_filters(task_type, old_values[task_type.id])
        return result

    def _create_or_update_dynamic_filters(self, task_type, old_values={}):
        legend_fields = ['legend_blocked', 'legend_normal', 'legend_done']
        for field in legend_fields:
            old_legend_value = old_values.get(field, False)
            new_legend_value = getattr(task_type, field)
            if old_legend_value and old_legend_value != new_legend_value:
                old_filter = self.env['ir.filters'].search([('name', '=', old_legend_value)], limit=1)
                if old_filter:
                    old_filter.write({'name': new_legend_value})
                    print(f"Updated filter with old value: {old_legend_value} to new value: {new_legend_value}")
            if new_legend_value:
                existing_filter = self.env['ir.filters'].search([('name', '=', new_legend_value)], limit=1)
                if existing_filter:
                    existing_filter.write({
                        'domain': [(field, '=', new_legend_value)],
                    })
                    print(f"Updated existing filter: {new_legend_value}")
                else:
                    filter_vals = {
                        'name': new_legend_value,
                        'model_id': 'project.task',
                        'domain': [(field, '=', new_legend_value)],
                        'context': {},
                        'is_default': False,
                        'user_id': False,
                        'sort': 'create_date desc',
                    }
                    self.env['ir.filters'].create(filter_vals)
                    print(f"Created new filter: {new_legend_value}")


