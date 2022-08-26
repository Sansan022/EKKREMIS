# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class team_configuration(models.Model):
    _name = 'team.configuration'
    _rec_name = 'team_number'

    team_number= fields.Char(string='Team number', required=True, copy=False, default='New') 
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
        if vals.get('team_number', 'New') == 'New':
            vals['team_number'] = self.env['ir.sequence'].next_by_code('team_sequence') or 'New'

        res =super(team_configuration,self).create(vals)

        for rec in res.team_members:
            rec.team_members_lines.write({'team_number_id': res.team_number})
            if rec.team_number == res.team_number:
                raise ValidationError('invalid')
            else:
                self.env['team.page.lines'].create({
                'team_page_lines': rec.team_members_lines.id,
                'team_number_team': res.team_number
            })
            

        return res

    @api.multi
    def write(self, values):
        res = super(team_configuration, self).write(values)

        for rec in self.team_members:
            rec.team_members_lines.write({'team_number_id': self.team_number})
            self.env['team.page.lines'].create({
            'team_page_lines': rec.team_members_lines.id,
            'team_number_team': self.team_number
        })
                
        return res

    # def history(self):
        
    #     for rec in self.team_members:
    #         rec.team_members_lines.write({'team_number_id': self.team_number})
    #         self.env['team.page.lines'].create({
    #             'team_page_lines': rec.team_members_lines.id,
    #             'team_number_team': self.team_number
    #         })

    # team_page_lines = fields.Many2one('hr.employee')
    # team_number_team = fields.Char()
           
       
       
                        
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

    @api.multi
    def write(self, vals):
        y = []
        x = self.env['team.configuration'].search([]).mapped('team_members')
        for rec in x:
            y.append(rec.team_members_lines.id)

        res = super(team_configuration_line, self).write(vals)

        if self.team_members_lines.id in y:
            raise ValidationError("Invalid team member")
        
        return res

    #validation for team members, one team only
    @api.onchange('team_members_lines')
    def _check_team_members(self):
        s = []
        x = self.env['team.configuration'].search([]).mapped('team_members')
        for rec in x:
            s.append(rec.team_members_lines.id)
        if self.team_members_lines.id in s:
            raise ValidationError("Invalid team member")


class team_page(models.Model):
    _inherit = 'hr.employee'
    _rec_name = 'team_number_id'

    history = fields.One2many('team.page.lines', 'team_page_lines')
    team_number_id = fields.Char(readonly=True)

    # @api.onchange('team_number_id')
    # def _onchange_team_number(self):
    #     lines = []
    #     for rec in self.history:
    #         for line in rec.team_page_lines:
    #             vals = {
    #                 'team_number': 12,
    #             }
    #             lines.append((0,0, vals))
    #         rec.history = lines
    #         print('---->',lines)

      
class team_page_lines(models.Model):  
    _name = 'team.page.lines'
    _rec_name = 'team_page_lines'

    team_page_lines = fields.Many2one('hr.employee')
    team_number_team = fields.Char()
    transaction_number = fields.Char()
    status = fields.Selection([
        ('permanent', 'Permanent'),
        ('temporary','Temporary')
    ],default='permanent')
