# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class team_configuration(models.Model):
    _name = 'team.configuration'
    _rec_name = 'sequence'

    sequence= fields.Char(string='Reference', readonly=True, required=True, copy=False, default='New') 
    team_number = fields.Integer()
    team_members = fields.One2many('team.configuration.line','team_members_lines1')

    _sql_constraints = [
    ('team_number', 'UNIQUE(team_number)', 'The team number already Exists!'),
]

    @api.model
    def create(self, vals):
        # if sequence data is equal to new 
        if vals.get('sequence', 'New') == 'New':
            vals['sequence'] = self.env['ir.sequence'].next_by_code('team_sequence') or 'New'
            return super(team_configuration, self).create(vals)

    @api.multi
    @api.onchange('team_members')
    def _check_team_members(self):
        s = []
        x = self.env['team.configuration'].search([]).mapped('team_members')
        for rec in x:
            s.append(rec.team_members_lines.id)
        try:
            if self.team_members.team_members_lines.id in s:
                raise ValidationError("Invalid2")
                print(s)
                print(self.team_members.team_members_lines.id )
        except:
            raise ValidationError("singleton error")
         
class team_configuration_line(models.Model):
    _name = 'team.configuration.line'
    # _rec_name = 'team_members_lines1'

    team_members_lines = fields.Many2one('hr.employee')
    team_members_lines1 = fields.Many2one('team.configuration')
   
class team_page(models.Model):
    _inherit = 'hr.employee'
    # _rec_name = 'team_number_lines'

    team_number_id = fields.Integer()
    history = fields.One2many('team.page.lines', 'team_page_lines')
    samp = fields.Many2one('team.configuration')

    @api.onchange('team_number_id')
    def _get_number_id(self):
        # id of employee
        ids = self._origin

        x = self.env['team.configuration'].search([]).mapped('team_members')
        y = []
        for rec in x:
            y.append(rec.team_members_lines.id)
            if ids.id in y:
                print('yes')
                print(rec.team_number)
            else:
                print('no')
        

class team_page_lines(models.Model):  
    _name = 'team.page.lines'
    _rec_name = 'team_page_lines'

    team_page_lines = fields.Many2one('hr.employee')
    team_number = fields.Integer()
    transaction_number = fields.Integer()
    status = fields.Selection([
        ('permanent', 'Permanent'),
        ('temporary','Temporary')
    ])
    


