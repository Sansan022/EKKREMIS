from odoo import models, fields, api

class team_configuration(models.Model):
    _name = 'team.configuration'


    sequence= fields.Char(string='Reference', readonly=True, required=True, copy=False, default='New') 
    team_number = fields.Integer()
    team_members = fields.One2many('team.configuration.line','team_members_lines')
    
    
    @api.model
    def create(self, vals):
        # if sequence data is equal to new 
        if vals.get('sequence', 'New') == 'New':
            vals['sequence'] = self.env['ir.sequence'].next_by_code('team_sequence') or 'New'
            res = super(team_configuration, self).create(vals)
            return res

class team_configuration_line(models.Model):
    _name = 'team.configuration.line'

    team_members_lines = fields.Many2one('hr.employee')
    team_members_id = fields.Many2one('hr.employee')

class team_page(models.Model):
    _inherit = 'hr.employee'
    team_number_lines = fields.Many2one('team.configuration')
    team_number_id = fields.Integer(related='team_number_lines.team_number')
    history = fields.One2many('team.page.lines', 'team_page_lines')
    
class team_page_lines(models.Model):  
    _name = 'team.page.lines'
    team_page_lines = fields.Many2one('hr.employee')
    team_number = fields.Integer()
    transaction_number = fields.Integer()
    status = fields.Selection([
        ('permanent', 'Permanent'),
        ('temporary','Temporary')
    ])
    
