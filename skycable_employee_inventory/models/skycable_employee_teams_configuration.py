# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class team_configuration(models.Model):
    _name = 'team.configuration'
    _rec_name = 'sequence'

    sequence= fields.Char(string='Reference', readonly=True, required=True, copy=False, default='New') 
    team_number = fields.Integer()
    team_members = fields.One2many('team.configuration.line','team_members_lines1')

    # check if team number already exist
    _sql_constraints = [
    ('team_number', 'UNIQUE(team_number)', 'The team number already Exists!'),
]

    @api.constrains('team_members')
    def _check_team_members_line(self):
        if len(self.team_members) == 0:
            raise ValidationError('Invalid, Empty team members!')

    @api.model
    def create(self, vals):
        # if sequence data is equal to new 
        if vals.get('sequence', 'New') == 'New':
            vals['sequence'] = self.env['ir.sequence'].next_by_code('team_sequence') or 'New'
            
            return super(team_configuration, self).create(vals)

    @api.multi
    def write(self, values):
        res = super(team_configuration, self).write(values)
        # here you can do accordingly
        
        # rec = self.env['hr.employee'].search([]).mapped('id')
        # for rec in self.team_members:
        #     # rec.team_number_id = values.get('team_number')
        #     rec.write({'team_number_id': self.team_number})
        #     print('yes')
        #     print(self.team_number)
        #     print(self.team_members)
        #     print(rec)

        record_ids = self.env['team.configuration.line'].search([('team_members_lines', '=', self.team_members.team_members_lines.id)])
        for record in record_ids:
            record.write({
            'team_number_id': self.team_number
        })
       
        return res


class team_configuration_line(models.Model):
    _name = 'team.configuration.line'
    _rec_name = 'team_members_lines'

    team_members_lines = fields.Many2one('hr.employee')
    team_members_lines1 = fields.Many2one('team.configuration')

    @api.model
    def create(self, vals):
        y = []
        x = self.env['team.configuration'].search([]).mapped('team_members')
        for rec in x:
            y.append(rec.team_members_lines.id)

        res = super(team_configuration_line, self).create(vals)

        if res.team_members_lines.id in y:
            raise ValidationError("Invalid")
        
        return res

    @api.model
    def write(self, vals):
        y = []
        x = self.env['team.configuration'].search([]).mapped('team_members')
        for rec in x:
            y.append(rec.team_members_lines.id)

        res = super(team_configuration_line, self).write(vals)

        if res.team_members_lines.id in y:
            raise ValidationError("Invalid")
        
        return res

    #validation for team members, one team only
    @api.onchange('team_members_lines')
    def _check_team_members(self):
        s = []
        x = self.env['team.configuration'].search([]).mapped('team_members')
        for rec in x:
            s.append(rec.team_members_lines.id)
        if self.team_members_lines.id in s:
            raise ValidationError("Invalid")


class team_page(models.Model):
    _inherit = 'hr.employee'
    # _rec_name = 'team_number_lines'

    history = fields.One2many('team.page.lines', 'team_page_lines')
    team_number_id = fields.Integer()

      
class team_page_lines(models.Model):  
    _name = 'team.page.lines'
    _rec_name = 'team_page_lines'

    team_page_lines = fields.Many2one('hr.employee')
    team_number = fields.Integer()
    transaction_number = fields.Integer()
    status = fields.Selection([
        ('permanent', 'Permanent'),
        ('temporary','Temporary')
    ],default='permanent')
    


