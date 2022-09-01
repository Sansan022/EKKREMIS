# @api.constrains('etsi_product_detail')
    # def check_unique_check(self):
    #     for rec in self.etsi_product_detail:
    #         etsi_serial_duplicate = self.env['etsi.inventory'].search_count([('etsi_serial', '=', rec.etsi_serials)])
    #         etsi_mac_duplicate = self.env['etsi.inventory'].search_count([('etsi_mac', '=', rec.etsi_macs)])
    #         if rec.etsi_serials == False and rec.etsi_macs == False:
    #             check3 = "Product must have either Serial NUmber or Mac Number"
    #             raise ValidationError(check3)
    #         if etsi_serial_duplicate >= 1:
    #             if etsi_serial_duplicate == False:
    #                 pass
    #             else:
    #                 check = "Duplicate detected within the database \n Serial Number: {}".format(rec.etsi_serials)
    #                 raise ValidationError(check)
    #         elif etsi_mac_duplicate >= 1:
    #             if etsi_mac_duplicate == False:
    #                 pass
    #             else:
    #                 check2 = "Duplicate detected within the database \n MAC Number: {}".format(rec.etsi_macs)
    #                 raise ValidationError(check2)

    # @api.constrains('etsi_product_detail_2')
    # def check_unique_check_2(self):
    #     for rec in self.etsi_product_detail_2:
    #         etsi_serial_duplicate_2 = self.env['etsi.inventory'].search_count([('etsi_serial', '=', rec.etsi_serials_2)])
    #         etsi_smart_duplicate_2 = self.env['etsi.inventory'].search_count([('etsi_smart_card', '=', rec.etsi_smart_card_2)])
    #         if rec.etsi_serials_2 == False and rec.etsi_smart_card_2 == False:
    #             check3 = "Product must have either Serial NUmber or Smart Card Number"
    #             raise ValidationError(check3)
    #         if etsi_serial_duplicate_2 >= 1:
    #             if etsi_serial_duplicate_2 == False:
    #                 pass
    #             else:
    #                 check = "Duplicate detected within the database \n Serial Number: {}".format(rec.etsi_serials_2)
    #                 raise ValidationError(check)
    #         elif etsi_smart_duplicate_2 >= 1:
    #             if etsi_serial_duplicate_2 == False:
    #                 pass
    #             else:
    #                 check2 = "Duplicate detected within the database \n Smart Card Number: {}".format(rec.etsi_smart_card_2)
    #                 raise ValidationError(check2)