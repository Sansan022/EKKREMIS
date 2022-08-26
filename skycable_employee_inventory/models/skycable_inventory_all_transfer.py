from odoo import api, fields, models
import time
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime



class EtsiTeams(models.Model):
    _inherit = "stock.picking"
    _rec_name = "etsi_teams_id"
    etsi_teams_id = fields.Many2one('team.configuration', string="Teams")
    etsi_teams_line_ids = fields.One2many(related="etsi_teams_id.team_members", string='Team Members', readonly=True)


