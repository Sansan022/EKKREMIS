# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Employee(models.Model):

    _inherit ='hr.employee'
    

    # Function galing kay etsi_hrms
    @api.model
    def default_get(self, fields):

        result = super(Employee, self).default_get(fields)
        ph_id = self.env.ref('base.ph').id
        if ph_id:
            result['country_id'] = ph_id
            # Dito default na niloload yung employee many2many tag(ex.  etsi_hrms.hr_emp_categ_employee, etsi_hrms.hr_emp_categ_trainee etc.)
            # Default Many2many category
            result['category_ids'] = [self.env.ref('etsi_hrms.hr_emp_categ_employee').id]

            # Default Many2one category

            
            result['emp_categ_id'] = [self.env.ref('etsi_hrms.hr_emp_categ_employee').id]
        

       
        return result






