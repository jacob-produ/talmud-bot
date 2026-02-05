import io


if __name__ == '__main__':
    packet = io.BytesIO()
    # pdfmetrics.registerFont(TTFont('hebrew', 'ahronbd.ttf'))
    # pdfmetrics.registerFont(TTFont('DAutomationSCMC7', 'IDAutomationSCMC7.ttf'))
    PaymentCheckFile.set_pdfmetrics_params()
    # reportlab.rl_config.TTFSearchPath.append('E:/check')
    export_path = os.path.join(DIR_PATH, 'assets/income')

    # create a new PDF with Reportlab
    header_data = {
        "account_num":"198000",
        "previous_account_num":"998000",
        "institution": u'שם המוסד בע"מ ע"מ'[::-1],
        "association":"xxxxxxxx",
        "mail":"xxxxxxxx",
        "phone_num":"052-1234567",
        "bank_branch_num":" 064",
        "bank_branch_name":u" סניף הרצל "[::-1],
        "bank_address": u" גולדה מאיר תל אביב "[::-1],
        "bank_phone_num": " 07123457689",
        "barcode":"80002010 10 685231 658721663"
    }

    body_data = {
        "addressee_name": u"מר ישראל ישראלי"[::-1],
        "amount":"1142",
        "amount_string":u"אלף"[::-1]
    }

    appendix_data = {
        "addressee_name": u"מר ישראל ישראלי"[::-1],
        "due_date": "02/07/2020",
        "amount":"1142",
        "check_num":"00000004",
        "month": "07",
        "trend_coordinator":"עמית כהן"[::-1],
        "check_num_indicator":"0/0"
    }

    footer_data = {
        "signature_img_path" : "Signature.JPG",
        "due_date": "02/07/2020",
        "barcode":"80002010 10 685231 658721663"
    }
    check_header = CheckHeader(account_num=header_data["account_num"],previous_account_num=header_data["previous_account_num"],
                             institution=header_data["institution"],association=header_data["association"],
                             phone_num=header_data["phone_num"],bank_branch_num=header_data["bank_branch_num"],
                             bank_branch_name=header_data["bank_branch_name"],bank_address=header_data["bank_address"],
                             bank_phone_num=header_data["bank_phone_num"],barcode=header_data["barcode"],
                             mail=header_data["mail"])
    check_body = CheckBody(addressee_name=body_data["addressee_name"],amount=body_data["amount"],amount_string=body_data["amount_string"])
    check_footer = CheckFooter(signature_file_name=footer_data["signature_img_path"],due_date=footer_data["due_date"],barcode=footer_data["barcode"])
    check_appendix = CheckAppendix(addressee_name=appendix_data["addressee_name"],amount=appendix_data["amount"],due_date=appendix_data["due_date"],
                                   check_num=appendix_data["check_num"],month=appendix_data["month"],
                                   trend_coordinator=appendix_data["trend_coordinator"],
                                   check_num_indicator=appendix_data["check_num_indicator"])


    check_list = []
    for i in range(7):
        check_list.append(PaymentCheck(header=check_header,body=check_body, footer=check_footer,appendix=check_appendix))
    check_file = PaymentCheckFile(checks=check_list,output_path=export_path, file_name="yae")
    check_file.dump()

