from odoo import models, fields

class User(models.Model):
    _inherit = 'res.users'
    
    def write(self, vals):
            if 'active' in vals and not vals['active']:
                for user in self:
                    self.env['project.project'].search([('user_id', '=', user.id)]).write({'user_id': False})
                    tasks_to_update = self.env['project.task'].search([('user_ids', 'in', user.ids)])
                    tasks_to_update.write({'user_ids': [(3, user.id)]})
                    follower_tasks = self.env['mail.followers'].search([
                        ('res_model', '=', 'project.task'),
                        ('partner_id', '=', user.partner_id.id)
                    ])
                    follower_tasks.unlink()
            return super(User, self).write(vals)