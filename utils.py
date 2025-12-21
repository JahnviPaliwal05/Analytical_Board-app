import pandas as pd
import os
from cleaned_data import *
import kaleido

def load_reviews():
    products_df = load_and_clean_products("data/products_reviews.csv")
    services_df = load_and_clean_services("data/services_reviews.csv")

    services = services_df
    products1 =products_df
    # You can merge multiple product datasets
    return pd.concat([services, products1], ignore_index=True)







def save_report(report_name, fig, summary_text):
    """
    Save the entire analytics report (figure + summary) as a PDF
    """
    os.makedirs("reports", exist_ok=True)

    # Save the Plotly figure as an image first
    fig_image_path = f"reports/{report_name}_figure.png"
    fig.write_image(fig_image_path, width=1200, height=600)

    # Create PDF
    pdf_file = f"reports/{report_name}.pdf"
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Title
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, f"Report: {report_name}", ln=True, align='C')

    pdf.ln(10)

    # Insert Figure
    pdf.image(fig_image_path, x=10, y=None, w=190)  # width 190mm (~A4 width minus margins)
    pdf.ln(10)

    # Insert Summary
    pdf.set_font("Arial", '', 12)
    pdf.multi_cell(0, 7, summary_text)

    # Save PDF
    pdf.output(pdf_file)

    return pdf_file


def list_reports():
    files = os.listdir("reports")
    reports = set([f.split(".pdf")[0] for f in files if f.endswith(".pdf")])
    return list(reports)


from fpdf import FPDF
import pandas as pd

def save_category_report_pdf(report_name, category, short_df, nps, best, worst, fig_curve, fig_pie, summary):
    os.makedirs("reports", exist_ok=True)

    # Save figures as images first
    fig_curve.write_image(f"reports/{report_name}_curve.png", width=1200, height=600, engine="kaleido", scale=2)
    fig_pie.write_image(f"reports/{report_name}_pie.png", width=800, height=600, engine="kaleido", scale=2)

    pdf_file = f"reports/{report_name}.pdf"
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Title
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, f"Report: {report_name}", ln=True, align='C')
    pdf.ln(5)
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, f"Category: {category}", ln=True)
    pdf.ln(5)

    # NPS
    pdf.cell(0, 10, f"NPS Score: {nps:.2f}%", ln=True)
    pdf.ln(5)

    # Tables (All Products)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, "All Products", ln=True)
    pdf.set_font("Arial", '', 10)
    for i, row in short_df.iterrows():
        pdf.multi_cell(0, 6, f"{row['name']}: Avg Rating = {row['avg_review_rating']:.2f}")
    pdf.ln(5)

    # Best Products
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, "Best Products", ln=True)
    pdf.set_font("Arial", '', 10)
    for i, row in best.iterrows():
        pdf.multi_cell(0, 6, f"{row['name']}: Avg Rating = {row['avg_review_rating']:.2f}")
    pdf.ln(5)

    # Worst Products
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, "Worst Products", ln=True)
    pdf.set_font("Arial", '', 10)
    for i, row in worst.iterrows():
        pdf.multi_cell(0, 6, f"{row['name']}: Avg Rating = {row['avg_review_rating']:.2f}")
    pdf.ln(5)

    # Happy Curve Figure
    pdf.image(f"reports/{report_name}_curve.png", x=10, w=190)
    pdf.ln(5)

    # Pie Chart
    pdf.image(f"reports/{report_name}_pie.png", x=10, w=150)
    pdf.ln(5)

    # Summary
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, "Summary of Unhappy Reviews", ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.multi_cell(0, 6, summary)

    pdf.output(pdf_file)
    with open(pdf_file, 'rb') as f:
        pdf_bytes = f.read()

    return pdf_file, pdf_bytes
    # return report_name,pdf_file

