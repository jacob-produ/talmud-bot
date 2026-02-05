from io import BytesIO
from num2words import num2words
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfbase.ttfonts import TTFont
import school_manager.constants.payment_check as pcc

from pdfrw import PdfReader, PdfWriter, PageMerge

class PaymentCheckGenerator:
    def __init__(self, details, output_path=pcc.OUTPUT_PAYMENT_FILE_PATH):
        self.details = details
        self.checks_count = 0
        self.current_page = 0
        self.packet = BytesIO()
        self.canvas = Canvas(self.packet, pagesize=A4)
        self.output_path = output_path
        # Set fonts.
        pdfmetrics.registerFont(TTFont('Aaroni', pcc.AARONI_FONT_PATH))
        pdfmetrics.registerFont(TTFont('Arial', pcc.ARIAL_FONT_PATH))
        pdfmetrics.registerFont(TTFont('IDAutomation', pcc.IDAUTOMATION_FONT_PATH))

        self.template_pdf = PdfReader(pcc.CHECK_TEMPLATE_FILE_PATH)
        self.page_width = int(round(float(self.template_pdf.pages[0]['/MediaBox'][2])))
        self.page_height = int(round(float(self.template_pdf.pages[0]['/MediaBox'][3])))
        self.output_pdf = Canvas(self.output_path, pagesize=(self.page_width, self.page_height))

    def generate(self):
        try:
            self._generate()
        except Exception as e:
            import traceback
            print(e)
            traceback.print_exc()

    def _generate(self):
        # Step 2: Load the template PDF
        writer = PdfWriter()

        # Step 3: Process the data, 4 checks per page
        for i in range(0, len(self.details), 4):

            # Get up to 4 rows of data for this page
            page_data = self.details.iloc[i:i + 4] if i + 4 < len(self.details) else self.details.iloc[i:]

            # Step 4: Create an overlay with the check data
            overlay_pdf_buffer = self.create_overlay(page_data)
            overlay_pdf = PdfReader(overlay_pdf_buffer)

            # Get the template page and merge with overlay
            template_page = self.template_pdf.pages[0].copy()
            overlay_page = overlay_pdf.pages[0]

            # Merge the overlay onto the template
            PageMerge(template_page).add(overlay_page).render()

            # Add the merged page to the writer
            writer.addpage(template_page)
        # Step 5: Save the final PDF with all checks
        writer.write(self.output_path)

    def prepare_data(self, data):
        data[pcc.AMOUNT_IN_WORDS] = num2words(data[pcc.AMOUNT], lang="heb").rjust(75)
        data[pcc.BANK_BRANCH_NUMBER] = str(data[pcc.BANK_BRANCH_NUMBER]).zfill(3)
        data[pcc.AMOUNT] = f"{data[pcc.AMOUNT]:,}"
        data[pcc.CREATE_DATE] = data[pcc.CREATE_DATE].strftime("%d/%m/%Y")
        data[pcc.BRANCH_AND_NUM] = f"{data[pcc.BANK_BRANCH_NAME][::-1]} {data[pcc.BANK_BRANCH_NUMBER]}".ljust(50)
        data[pcc.BANK_PHONE_AND_ADDRESS] = f"{data[pcc.BANK_MAIL_ADDRESS][::-1]} {data[pcc.BANK_PHONE]}".ljust(50)
        data[pcc.ACCOUNT_DETAILS] = f"{data[pcc.CHECK_NUMBER]} {data[pcc.BANK_NUM]} {data[pcc.BANK_BRANCH_NUMBER]} {data[pcc.BANK_ACCOUNT_NUMBER]}"
        data[pcc.BARCODE] = f"A{data[pcc.CHECK_NUMBER]} C{data[pcc.BANK_NUM]}E{data[pcc.BANK_BRANCH_NUMBER]} {data[pcc.BANK_ACCOUNT_NUMBER]}C"

    def create_overlay(self, data):
        """
        Create an overlay with check data for up to 4 checks per page.
        """
        buffer = BytesIO()
        c = Canvas(buffer, pagesize=(self.page_width, self.page_height))
        check_count = 0

        # Draw up to 4 checks on the overlay
        for idx, row in data.iterrows():
            margin = pcc.MARGIN[check_count % 4]
            self.prepare_data(row)
            for field_name, field_settings in pcc.INPUT_POS_DATA.items():
                for settings in field_settings:
                    x, y = settings[pcc.START_COORDINATES]
                    y = y - margin
                    c.setFont(*settings[pcc.FONT])

                    if field_name == pcc.SIGNATURE:
                        c.drawImage(pcc.SIGNATURE_FILE_PATH, x, y, width=20 * 72 / 25.4, height=8 * 72 / 25.4, preserveAspectRatio=True)
                    else:
                        if settings[pcc.RTL]:
                            c.drawRightString(x, y, str(row[field_name])[::-1])
                        else:
                            c.drawString(x, y, str(row[field_name]))


            check_count += 1

        c.save()
        buffer.seek(0)
        return buffer

