from odoo import api, fields, models
import time
from odoo.exceptions import ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime



class EtsiTeams(models.Model):
    _inherit = "stock.picking"
    _rec_name = "etsi_teams_id"
    etsi_teams_id = fields.Many2one('team.configuration', string="Teams Number")
    etsi_teams_member_no = fields.Char(string="Employee Number")
    etsi_teams_line_ids = fields.One2many(
    'team.replace','etsi_teams_replace_line', string='Team Members') 
    
    @api.multi
    @api.onchange('etsi_teams_member_no')
    def auto_fill_details_transfer(self): 
        for rec in self:
            database = self.env['hr.employee'].search([('identification_id','=',rec.etsi_teams_member_no)])
            database2 = self.env['team.configuration'].search([('team_number','=',database.team_number_id)])
            rec.etsi_teams_id = database2.id

    @api.multi
    @api.onchange('etsi_teams_id')
    def auto_fill_details_all_transfer2(self):
        table=[]
        for rec2 in self.etsi_teams_id.team_members:
            table.append((0,0,{
            'team_members_lines': rec2.team_members_lines,
            'etsi_teams_replace' :'' ,
            'etsi_teams_temporary' : '',
            }))
        self.etsi_teams_line_ids = table
        
    @api.model 
    def create(self, vals):
        
        
        res =super(EtsiTeams,self).create(vals)
        for line in res.etsi_teams_line_ids:
            if line.etsi_teams_temporary is False:
           
                self.env['team.page.lines'].create({
                'team_page_lines':  line.team_members_lines.id,
                'team_number_team': res.etsi_teams_id.team_number,
                'transaction_number': res.origin,
                'status': 'Permanent',
                })
            else:
                # for rec in self.team_configuration_id:
                #     rec.employee_id.write({'history_team_number': self.team_number})
                self.env['team.page.lines'].create({
                'team_page_lines':  line.etsi_teams_replace.id,
                'team_number_team': res.etsi_teams_id.team_number,
                'transaction_number': res.origin,
                'status': 'Temporary',
                 })
        return res

class EtsiTeamsReplace(models.Model):
    _name = "team.replace"
    # _inherit = 'team.configuration.line'
    etsi_teams_replace_line = fields.Many2one('stock.picking')
    team_members_lines = fields.Many2one('hr.employee', string="Team Member")
    etsi_teams_replace = fields.Many2one('hr.employee', string="Replaced Member")
    etsi_teams_temporary = fields.Boolean(string="Temporary Team")

    
    # etsi_teams_id_line = fields.Many2one('team.configuration.line', string="Teams")
    # etsi_team_members_lines = fields.Many2one('stock.picking', related="etsi_teams_id_line.team_members_lines1")
    # team_members_lines = fields.Many2one(related="etsi_teams_id_line.team_members_lines")

    @api.constrains('etsi_teams_replace','etsi_teams_temporary')
    def check(self):
        if self.etsi_teams_temporary == True:
            if len(self.etsi_teams_replace) == 0:
                raise ValidationError("No Replaced Member selected!")
    

   