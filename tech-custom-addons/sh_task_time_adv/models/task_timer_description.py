from odoo import api, models, fields
from odoo.exceptions import AccessError

class TaskTimerDescription(models.Model):
    _name = 'task.timer.description'
    _description = 'Task Timer Description'

    name = fields.Char("Name", required=True)
