from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError

class OperationReturn(models.TransientModel):
    _inherit = "stock.return.picking"
    
    serial_holder_id = fields.One2many('stock.return.picking.line.return.serial','serial_holder_ids', string="Return List")
    
    @api.model
    def create(self, vals):
        print('CREATE..........')
        if 'serial_holder_id' in vals:
            # TEMPORARY DATA - FOR TESTING PURPOSES
            var_serial = "1234566"
            var_mac = "123123"
            var_card = "124124"
            
            for lines in vals['serial_holder_id']:
                get_dict = lines[2]
                if get_dict:
                    if get_dict['etsi_serial_product'] != var_serial:
                        raise ValidationError('HULI KA BALBON')
        
        return super(OperationReturn, self).create(vals)
    
    @api.multi
    def write(self, vals):
        return super(OperationReturn, self).write(vals)
        
class OperationReturnLine(models.TransientModel):
    _inherit = 'stock.return.picking.line'
    
    etsi_serial_product = fields.Char(string="Serial ID")
    etsi_mac_product = fields.Char(string="MAC ID")
    etsi_smart_card = fields.Char(string="Smart Card")
    
    
    
class OperationReturnLineTwo(models.TransientModel):
    _name = 'stock.return.picking.line.return.serial'
    
    serial_holder_ids = fields.Many2one('stock.return.picking')
    etsi_serial_product = fields.Char(string="Serial ID")
    etsi_mac_product = fields.Char(string="MAC ID")
    etsi_smart_card = fields.Char(string="Smart Card")
    
    