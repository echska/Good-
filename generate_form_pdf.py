"""
Generate a cargo document PDF inspired by the provided template.

This script constructs a PDF document similar in style to the sample
“طباعة الوثيقة” template. It draws a header with document details,
includes the Iraq Customs logo, lays out a table with labels on the
right-hand side and blanks on the left for data, and adds a footer
notice.  The script uses ReportLab for PDF generation and embeds the
Cairo font to support Arabic text.

To customise the output, edit the `sample_data` dictionary in the
`__main__` block. Each key corresponds to one of the labelled fields
in the template.  Running the script will produce a file named
`generated_document.pdf` in the current directory.

Note: Proper Arabic shaping normally requires libraries such as
arabic_reshaper and python-bidi.  These libraries are not available
in this environment, so Arabic text will be drawn in isolated glyphs.
This script nevertheless uses the Cairo font to render Arabic letters
cleanly.  For production use, consider integrating arabic_reshaper
and bidi for correct shaping and ordering.
"""

import os
from typing import Dict

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import mm
from PIL import Image


def register_fonts() -> None:
    """Register fonts capable of rendering Arabic text.

    ReportLab does not natively ship with Arabic-supporting fonts, so
    we register the DejaVu Sans family from the system fonts directory.
    DejaVu Sans includes Arabic glyphs and works reasonably well for
    basic right-to-left scripts, although proper shaping is still
    required for accurate rendering (see module docstring).
    """
    # Attempt to locate DejaVu Sans fonts in common system paths
    potential_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]
    font_names = ["DejaVuSans", "DejaVuSans-Bold"]
    for path, name in zip(potential_paths, font_names):
        if os.path.exists(path):
            pdfmetrics.registerFont(TTFont(name, path))


def draw_header(c: canvas.Canvas, logo_path: str, doc_number: str, doc_date: str, doc_time: str) -> None:
    """Draw the document header, including logo and metadata."""
    width, height = A4  # 595 x 842 points
    # Right-hand side header: government text
    government_text = ["جمهورية العراق", "وزارة المالية", "الهيئة العامة للكمارك"]
    c.setFont("DejaVuSans-Bold", 10)
    text_y = height - 20
    for line in government_text:
        c.drawRightString(width - 30, text_y, line)
        text_y -= 12

    # Left-hand side header: document metadata
    meta_labels = ["رقم الوثيقة", "تاريخ إنشاء الوثيقة", "التوقيت"]
    meta_values = [doc_number, doc_date, doc_time]
    c.setFont("DejaVuSans-Bold", 10)
    meta_y = height - 20
    for label, value in zip(meta_labels, meta_values):
        # Draw value right aligned relative to a small column
        c.drawString(30, meta_y, value)
        c.drawRightString(150, meta_y, label)
        meta_y -= 12

    # Center logo
    if logo_path and os.path.exists(logo_path):
        # Resize the logo to a reasonable size (e.g., 40 mm width)
        logo_width_mm = 40
        logo_height_mm = 40
        logo_width = logo_width_mm * mm
        logo_height = logo_height_mm * mm
        logo_x = (width - logo_width) / 2
        logo_y = height - 70  # position below the top margin
        c.drawImage(logo_path, logo_x, logo_y, width=logo_width, height=logo_height, mask='auto')

    # Draw a thin horizontal line below header
    c.setLineWidth(0.5)
    c.line(30, height - 95, width - 30, height - 95)


def draw_title(c: canvas.Canvas) -> None:
    """Draw the document title and subtitle."""
    width, height = A4
    c.setFont("DejaVuSans-Bold", 14)
    c.drawCentredString(width / 2, height - 120, "منصة المنتج المحلي")
    c.setFont("DejaVuSans-Bold", 10)
    subtitle = "الموضوع / الوثيقة المؤقتة لبيانات الحمولة من قبل الشركة"
    c.drawCentredString(width / 2, height - 140, subtitle)


def draw_table(c: canvas.Canvas, data: Dict[str, str]) -> None:
    """Draw the information table.

    Args:
        c: ReportLab canvas
        data: Dictionary containing values for each field. Expected keys:
            entry_control_name, driver_name, vehicle_number,
            registration_province, cargo_details, total_weight,
            destination, province_name, company_name,
            weight_authority, ministry_number, ministry_date,
            ministry_port, trademark, licensed_products
    """
    width, height = A4
    # Define starting position
    table_x = 30
    table_y = height - 180
    table_width = width - 60  # margin 30 each side
    # Column widths: left (values) vs right (labels)
    label_col_width = 180
    value_col_width = table_width - label_col_width
    row_height = 20

    # Define rows: (label_key, data_key)
    rows = [
        ("اسم سيطرة الدخول", "entry_control_name"),
        ("اسم السائق", "driver_name"),
        ("رقم العجلة", "vehicle_number"),
        ("محافظة تسجيل العجلة", "registration_province"),
        ("نوع تفاصيل الحمولة", "cargo_details"),
        ("الوزن الكلي", "total_weight"),
        ("الوجهة الصناعية / المحافظة", "destination"),
        ("اسم المحافظة", "province_name"),
        ("اسم الشركة / المشروع", "company_name"),
        ("الجهة المعدة للوزن / الموافقة", "weight_authority"),
        ("رقم الوزارة / الموافقة", "ministry_number"),
        ("تاريخ الوزارة / الموافقة", "ministry_date"),
        ("منفذ الوزارة / الاختصاص", "ministry_port"),
        ("العلامة التجارية", "trademark"),
    ]

    # Draw header row background
    c.setFillColor(colors.HexColor("#9A0E14"))  # deep red
    c.rect(table_x, table_y + row_height * len(rows) + row_height, table_width, row_height, stroke=0, fill=1)
    # Header text
    c.setFillColor(colors.white)
    c.setFont("DejaVuSans-Bold", 11)
    c.drawCentredString(table_x + table_width / 2, table_y + row_height * len(rows) + row_height + 5, "المعلومات الشخصية")

    # Draw rows
    c.setFont("DejaVuSans", 10)
    c.setFillColor(colors.black)
    for idx, (label, key) in enumerate(rows):
        y = table_y + row_height * (len(rows) - idx)
        # Row lines
        c.setLineWidth(0.25)
        c.setStrokeColor(colors.black)
        # Horizontal line
        c.line(table_x, y, table_x + table_width, y)
        # Vertical lines
        c.line(table_x + value_col_width, y, table_x + value_col_width, y - row_height)
        # Label
        c.drawRightString(table_x + table_width - 5, y - row_height + 6, label)
        # Value
        value = data.get(key, "")
        c.drawString(table_x + 5, y - row_height + 6, value)

    # Draw bottom horizontal line for final row
    c.line(table_x, table_y, table_x + table_width, table_y)

    # Draw licensed products header
    licensed_y = table_y - row_height
    c.setFillColor(colors.HexColor("#9A0E14"))
    c.rect(table_x, licensed_y, table_width, row_height, stroke=0, fill=1)
    c.setFillColor(colors.white)
    c.setFont("DejaVuSans-Bold", 11)
    c.drawCentredString(table_x + table_width / 2, licensed_y + 5, "المواد / المنتجات المرخصة")

    # Draw products area box (spans both columns)
    products_height = 80
    c.setFillColor(colors.white)
    c.rect(table_x, licensed_y - products_height, table_width, products_height, stroke=1, fill=0)
    # Fill products text
    c.setFillColor(colors.black)
    c.setFont("DejaVuSans", 9)
    products_text = data.get("licensed_products", "")
    text_x = table_x + 5
    text_y = licensed_y - 15
    # Wrap the text manually into multiple lines if necessary
    max_chars_per_line = 90
    lines = []
    current_line = ""
    for word in products_text.split():
        if len(current_line) + len(word) + 1 > max_chars_per_line:
            lines.append(current_line)
            current_line = word
        else:
            if current_line:
                current_line += " " + word
            else:
                current_line = word
    if current_line:
        lines.append(current_line)
    for ln in lines:
        c.drawString(text_x, text_y, ln)
        text_y -= 12


def draw_footer(c: canvas.Canvas) -> None:
    """Draw the footer notice and (optional) coat-of-arms.

    The note text informs the user about keeping the document for
    reference and provides a URL for more information.  The coat of
    arms image is not embedded in this version, but the function
    reserves space for it on the bottom right.
    """
    width, height = A4
    # Notice text (wrap as needed)
    notice_lines = [
        "إن احتفاظك بهذه الوثيقة يحفظ حقوقك في استخدامها لدى الجهات المرتبطة بالنظام.",
        "يمكنك حفظ صور الوثيقة في الهاتف لاستخدامها عند الحاجة.",
        "لمزيد من المعلومات عن الخدمات الحكومية الإلكترونية يمكنك زيارة:",
        "https://ur.gov.iq",
    ]
    c.setFont("DejaVuSans", 7)
    c.setFillColor(colors.black)
    y = 100
    for ln in notice_lines[:-1]:
        c.drawCentredString(width / 2, y, ln)
        y -= 10
    # Link line in blue
    c.setFillColor(colors.HexColor("#0070c0"))
    c.drawCentredString(width / 2, y, notice_lines[-1])

    # English credit text at bottom left
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 6)
    c.drawString(30, 40, "Prime Minister's Office")
    c.drawString(30, 30, "National Center for Digital Transformation")
    c.drawString(30, 20, "Tel: 5599")

    # Optional coat-of-arms space at bottom right (left blank)
    # If a path to the coat-of-arms image is known, it can be drawn here.


def generate_document(output_path: str, logo_path: str, data: Dict[str, str]) -> None:
    """Generate the PDF document using the provided data."""
    register_fonts()
    c = canvas.Canvas(output_path, pagesize=A4)
    # Draw header and body
    draw_header(c, logo_path, data.get("doc_number", ""), data.get("doc_date", ""), data.get("doc_time", ""))
    draw_title(c)
    draw_table(c, data)
    draw_footer(c)
    c.showPage()
    c.save()


if __name__ == "__main__":
    # Sample data to populate the form
    sample_data = {
        "doc_number": "19063",
        "doc_date": "26-01-2026",
        "doc_time": "09:24 PM",
        "entry_control_name": "سيطرة أربيل",
        "driver_name": "أحمد محمد",
        "vehicle_number": "12345",
        "registration_province": "أربيل",
        "cargo_details": "حبوب غذائية",
        "total_weight": "15 طن",
        "destination": "بغداد / الرصافة",
        "province_name": "بغداد",
        "company_name": "معمل الغذاء",
        "weight_authority": "هيئة المقاييس",
        "ministry_number": "54321",
        "ministry_date": "25-01-2026",
        "ministry_port": "منفذ فايدا",
        "trademark": "العلامة التجارية XYZ",
        "licensed_products": "قمح، شعير، عدس، أرز",
    }
    # Use the extracted logo from the sample PDF; if not present, leave blank
    base_dir = os.path.dirname(__file__)
    logo_file = os.path.join(base_dir, "logo_big.png") if os.path.exists(os.path.join(base_dir, "logo_big.png")) else ""
    output_pdf = os.path.join(base_dir, "generated_document.pdf")
    generate_document(output_pdf, logo_file, sample_data)
    print(f"Generated PDF saved to {output_pdf}")