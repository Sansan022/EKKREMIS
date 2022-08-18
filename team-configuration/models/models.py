# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class team_configuration(models.Model):
    _name = 'team.configuration'
    _rec_name = 'sequence'


    sequence= fields.Char(string='Reference', readonly=True, required=True, copy=False, default='New') 
    team_number = fields.Integer()
    team_members = fields.One2many('team.configuration.line','team_members_lines1')


    _sql_constraints = [
    ('name', 'unique (team_number)', 'The team_number already Exists!'),
]

#    @api.model
#     def create(self, values):
#         res = super(ResPartner, self).create(values)
#         # here you can do accordingly
#         self.team_number
#         return res

     
    @api.model
    def create(self, vals):
        # if sequence data is equal to new 
        if vals.get('sequence', 'New') == 'New':
            vals['sequence'] = self.env['ir.sequence'].next_by_code('team_sequence') or 'New'
            res = super(team_configuration, self).create(vals)
            return res

     
    # @api.onchange('team_members')
    # def _check_team_members(self):
    #     x = self.env['team.configuration'].search([]).mapped('team_members')
    #     for rec in x:
    #         if rec.team_members_lines.id == self.team_members.team_members_lines.id:
    #             raise ValidationError("Invalid")

    #     print('x',rec.team_members_lines.name)
    #     print('member',self.team_members.team_members_lines.name)  
     
    @api.multi
    @api.onchange('team_members')
    def _check_team_members(self):
        s = []
        x = self.env['team.configuration'].search([]).mapped('team_members')
        for rec in x:
            s.append(rec.team_members_lines.id)
        try:
            if self.team_members.team_members_lines.id in s:
                raise ValidationError("Invalid")
        except:
            raise ValidationError("Invalid")
            

class team_configuration_line(models.Model):
    _name = 'team.configuration.line'
    _rec_name = 'team_members_lines'

    team_members_lines = fields.Many2one('hr.employee')
    team_members_lines1 = fields.Many2one('team.configuration')

   
class team_page(models.Model):
    _inherit = 'hr.employee'
    _rec_name = 'team_number_lines'

    team_number_lines = fields.Many2one('team.configuration')
    team_number_id = fields.Integer(related='team_number_lines.team_number')
    history = fields.One2many('team.page.lines', 'team_page_lines')


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
    


