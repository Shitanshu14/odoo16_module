from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'


    type_id = fields.Many2one('hr.contract.type', string="Employee Category")
    structure_type_id = fields.Many2one('hr.payroll.structure', string="Salary Structure")
    contract_type_id = fields.Many2one('hr.contract.type', string="Contract Type")
    resource_calendar_id = fields.Many2one('resource.calendar', string="Working Schedule")
    analytic_account_id = fields.Many2one('account.analytic.account', string="Analytic Account")
    journal_id = fields.Many2one('account.journal', string="Salary Journal")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        type_id = self.env['ir.config_parameter'].sudo().get_param('ts_recruitment_contract.type_id', default=False)
        structure_type_id = self.env['ir.config_parameter'].sudo().get_param('ts_recruitment_contract.structure_type_id', default=False)
        contract_type_id = self.env['ir.config_parameter'].sudo().get_param('ts_recruitment_contract.contract_type_id', default=False)
        resource_calendar_id = self.env['ir.config_parameter'].sudo().get_param('ts_recruitment_contract.resource_calendar_id', default=False)
        analytic_account_id = self.env['ir.config_parameter'].sudo().get_param('ts_recruitment_contract.analytic_account_id', default=False)
        journal_id = self.env['ir.config_parameter'].sudo().get_param('ts_recruitment_contract.journal_id', default=False)

        res.update(
            type_id=int(type_id) if type_id else False,
            structure_type_id=int(structure_type_id) if structure_type_id else False,
            contract_type_id=int(contract_type_id) if contract_type_id else False,
            resource_calendar_id=int(resource_calendar_id) if resource_calendar_id else False,
            analytic_account_id=int(analytic_account_id) if analytic_account_id else False,
            journal_id=int(journal_id) if journal_id else False
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('ts_recruitment_contract.type_id', self.type_id.id or False)
        self.env['ir.config_parameter'].sudo().set_param('ts_recruitment_contract.structure_type_id', self.structure_type_id.id or False)
        self.env['ir.config_parameter'].sudo().set_param('ts_recruitment_contract.contract_type_id', self.contract_type_id.id or False)
        self.env['ir.config_parameter'].sudo().set_param('ts_recruitment_contract.resource_calendar_id', self.resource_calendar_id.id or False)
        self.env['ir.config_parameter'].sudo().set_param('ts_recruitment_contract.analytic_account_id', self.analytic_account_id.id or False)
        self.env['ir.config_parameter'].sudo().set_param('ts_recruitment_contract.journal_id', self.journal_id.id or False)

