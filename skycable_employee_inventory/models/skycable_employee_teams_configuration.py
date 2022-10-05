# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class team_configuration(models.Model):
    _name = 'team.configuration'
    _rec_name = 'team_number'

    team_number= fields.Char(string='Team Code', required=True, copy=False, default='New') 
    team_members = fields.One2many('team.configuration.line','team_members_lines1')
    teamType = fields.Selection([
        ('one_man', "1-man Team"),
        ('two_man', "2-man Team"),
    ], default='one_man')

    # check if team number already exist
    _sql_constraints = [
    ('team_number', 'UNIQUE(team_number)', 'The team number already Exists!'),
]

     # check the length of team 
    @api.constrains('team_members')
    def _limitTeamMembers(self):
        if self.teamType == 'two_man': 
            if len(self.team_members) > 2:
                raise ValidationError("Exceed the maximum number of member(2).")
        
        if self.teamType == 'one_man': 
            if len(self.team_members) > 1:
                raise ValidationError("Exceed the maximum number of member(1).")

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



            self.env['team.page.lines'].create({
            'team_page_lines': rec.team_members_lines.id,
            'team_number_team': res.team_number,
            'status': 'permanent',
            'teamTypeHistory': self.teamType,
            })
            
            

        return res

    @api.multi
    def write(self, values):
        res = super(team_configuration, self).write(values)
        b = []
        c = []
        temp3 = []
        a = self.env['hr.employee'].search([('team_number_id','=',self.team_number)])   
        for recs in a:
            b.append(recs.id)

        for rec in self.team_members:
            rec.team_members_lines.write({'team_number_id': self.team_number})
            c.append(rec.team_members_lines.id)
            self.env['team.page.lines'].create({
                'team_page_lines': rec.team_members_lines.id,
                'team_number_team': self.team_number,
                'status': 'Permanent',
                'teamTypeHistory': self.teamType,
            })

        for element in b:
            if element not in c:
                temp3.append(element)

        for removed in temp3:
            self.env['hr.employee'].search([('id','=',removed)]).write({'team_number_id': ''}) 
            self.env['team.page.lines'].create({
                'team_page_lines': removed,
                'team_number_team': self.team_number,
                'status': 'Removed'
            })
      
        return res

                        
class team_configuration_line(models.Model):
    _name = 'team.configuration.line'
    # _rec_name = 'team_members_lines'

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
            raise ValidationError("Selecting same employee is not allowed!")
        
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
            raise ValidationError("Employee already part of a team!")


class team_page(models.Model):
    _inherit = 'hr.employee'
    # _rec_name = 'team_number_id'

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
    # _rec_name = 'team_page_lines'

    team_page_lines = fields.Many2one('hr.employee')
    team_number_team = fields.Char()
    transaction_number = fields.Char()
    status = fields.Char()
    teamTypeHistory = fields.Selection([
        ('one_man', "1-man Team"),
        ('two_man', "2-man Team"),
    ], default='one_man')