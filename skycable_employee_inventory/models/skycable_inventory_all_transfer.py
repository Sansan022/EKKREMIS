from odoo import api, fields, models
import time
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime



class EtsiTeams(models.Model):
    _inherit = "stock.picking"
    _rec_name = "etsi_teams_id"
    etsi_subscriber_issuance = fields.Integer()
    etsi_team_issuance = fields.Integer()
    etsi_teams_id = fields.Many2one('team.configuration', string="Teams")
    etsi_teams_line_ids = fields.One2many(related="etsi_teams_id.team_members", string='Team Members', readonly=True)

    
    etsi_subscriber = fields.Boolean()
    
    @api.onchange('picking_type_id')
    def _onchange_picking_type_id(self):
        for rec in self:
            if rec.picking_type_id.subscriber_checkbox:
                rec.etsi_subscriber = rec.picking_type_id.subscriber_checkbox
                
                
                
    @api.multi
    def get_subscriber_issuance(self):
        return {
            'name': 'Subscriber Issuance',
            'res_model': 'stock.picking',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'domain': [('location_dest_id', '!=', 'Team Location')]
        }
    def get_team_issuance(self):
        return {
            'name': 'Team Issuance',
            'res_model': 'stock.picking',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'domain': [('location_dest_id', '=', 'Team Location')]
        } 
