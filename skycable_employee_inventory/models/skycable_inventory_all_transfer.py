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
    def auto_fill_details_01(self): 
        for rec in self:
            database = self.env['hr.employee'].search([('identification_id','=',rec.etsi_teams_member_no)])
            database2 = self.env['team.configuration'].search([('team_number','=',database.team_number_id)])
            rec.etsi_teams_id = database2.id

    @api.multi
    @api.onchange('etsi_teams_id')
    def auto_fill_details_02(self):
        table=[]
        for rec2 in self.etsi_teams_id.team_members:
            table.append((0,0,{
            'team_members_lines': rec2.team_members_lines,
            'etsi_teams_replace' :'' ,
            'etsi_teams_temporary' : '',
            }))
        self.etsi_teams_line_ids = table
        
    # @api.model 
    # def create(self, vals):
        
        
    #     res =super(EtsiTeams,self).create(vals)
    #     for line in res.etsi_teams_line_ids:
    #         if line.etsi_teams_temporary is False:
           
    #             self.env['team.page.lines'].create({
    #             'team_page_lines':  line.team_members_lines.id,
    #             'team_number_team': res.etsi_teams_id.team_number,
    #             'transaction_number': res.origin,
    #             'status': 'Permanent',
    #             })
    #         else:
    #             # for rec in self.team_configuration_id:
    #             #     rec.employee_id.write({'history_team_number': self.team_number})
    #             self.env['team.page.lines'].create({
    #             'team_page_lines':  line.etsi_teams_replace.id,
    #             'team_number_team': res.etsi_teams_id.team_number,
    #             'transaction_number': res.origin,
    #             'status': 'Temporary',
    #              })
    #     return res

    @api.multi
    def do_new_transfer(self):
        res = super(EtsiTeams,self).do_new_transfer()
        for line in self.etsi_teams_line_ids:
            if line.etsi_teams_temporary is False:
            
                self.env['team.page.lines'].create({
                'team_page_lines':  line.team_members_lines.id,
                'team_number_team': self.etsi_teams_id.team_number,
                'transaction_number': self.name,
                'status': 'Permanent',
                })
            else:
                # for rec in self.team_configuration_id:
                #     rec.employee_id.write({'history_team_number': self.team_number})
                self.env['team.page.lines'].create({
                'team_page_lines':  line.etsi_teams_replace.id,
                'team_number_team': self.etsi_teams_id.team_number,
                'transaction_number': self.name,
                'status': 'Temporary',
                    })
        return res
    
    
    # Smartbutton functions
    etsi_subscriber_issuance = fields.Integer(compute='_subs_issuance_count')
    etsi_team_issuance = fields.Integer(compute="_team_issuance_count")
    etsi_subscriber = fields.Boolean()
    
    @api.onchange('picking_type_id')
    def _onchange_picking_type_id(self):
        for rec in self:
            if rec.picking_type_id.subscriber_checkbox == True:
                rec.etsi_subscriber = rec.picking_type_id.subscriber_checkbox
                
    
                
    @api.multi
    def get_subscriber_issuance(self):
        return {
            'name': 'Subscriber Issuance',
            'res_model': 'stock.picking',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'domain': [('picking_type_id.code','=','outgoing')]
        }
    def _subs_issuance_count(self): 
        data_obj = self.env['stock.picking']
        for data in self:       
            list_data = data_obj.search([('partner_id','!=', False)])
            data.etsi_subscriber_issuance = len(list_data)     
        
    def get_team_issuance(self):
        return {
            'name': 'Team Issuance',
            'res_model': 'stock.picking',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'domain': [('picking_type_id.code','=','internal')]
        } 
    def _team_issuance_count(self): 
        data_obj = self.env['stock.picking']
        for data in self:       
            list_data = data_obj.search([('partner_id','=', False)])
            data.etsi_team_issuance = len(list_data)
            
    # End Smartbutton functions






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

    @api.onchange('etsi_teams_temporary')
    def onchange_replaced_id(self):
        for request in self:
            domain = {}
            if self.etsi_teams_temporary == True:
                if request.team_members_lines:
                    task_list = []
                    task_obj = self.env['hr.employee'].search([])
                    if task_obj:
                        for task in task_obj:
                            if task.team_number_id == request.team_members_lines.team_number_id:
                                task_list.append(task.team_number_id)
                        if task_list:
                            domain['etsi_teams_replace'] =  [('team_number_id', 'not in', task_list)]
                        else:
                            domain['etsi_teams_replace'] =  []

                return {'domain': domain}
    

   