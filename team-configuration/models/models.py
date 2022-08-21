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

    @api.model
    def create(self, vals):
        # if sequence data is equal to new 
        if vals.get('sequence', 'New') == 'New':
            vals['sequence'] = self.env['ir.sequence'].next_by_code('team_sequence') or 'New'
        return super(team_configuration, self).create(vals)
   

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
        print('vals--->', vals)
        print('res--->', res.team_members_lines.id)
    
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
        print('vals--->', vals)
        print('res--->', res.team_members_lines.id)
    
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
    samp = fields.Many2one('team.configuration')
    aye = fields.Integer(related='samp.team_number',string='related to samp')
    team_number_id = fields.Integer(default=aye)

    @api.model
    def create(self, values):
        res = super(ResPartner, self).create(values)
        # here you can do accordingly
        return res


    @api.multi
    def write(self, values):
        res = super(ResPartner, self).write(values)
        # here you can do accordingly
        return res

    # get team number id in team configuration to team page
    # @api.onchange('team_number_id')
    # def _get_number_id(self):
    #     id of employee
    #     ids = self._origin

    #     x = self.env['team.configuration'].search([]).mapped('team_members')
    #     z = self.env['team.configuration'].search([]).mapped('team_number')
    #     for rec in z:
    #         print('rec of z',rec)
    #         print('rec of z',rec)
    #     y = []
    #     for rec in x:
    #         y.append(rec.team_members_lines.id)
    #         if ids.id in y:
    #             print('yes')
    #             print(ids.id)
    #         else:
    #             print('no')
        

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
    


