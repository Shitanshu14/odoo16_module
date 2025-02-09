from odoo import fields, models, api

class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'
    _description = 'Maintenance Equipment'

    @api.model
    def create(self,vals):
        #Sequence Settings
        vals['serial_no'] = self.env['ir.sequence'].next_by_code('equipment.sequence.technians')
        res_id = super(MaintenanceEquipment, self).create(vals)
        return res_id