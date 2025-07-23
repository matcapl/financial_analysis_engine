import fitz  # PyMuPDF
import re
import os
import pandas as pd
from pathlib import Path


def extract_text_from_pdf(pdf_path: str) -> str:
    doc = fitz.open(pdf_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    return full_text


def clean_and_split_sections(text: str):
    sections = re.split(r"(?=Wilson Partners Consolidation\s+Management Reports February 2025\s+STATUTORY BASIS)", text)
    return [s.strip() for s in sections if s.strip()]


def extract_table_blocks(section: str):
    blocks = {}
    # Each main report type
    titles = [
        "Monthly P&L comparison to budget and prior year",
        "YTD P&L comparison to budget and prior year",
        "LTM P&L comparison to budget and prior year",
        "Balance sheet comparison to prior month and budget",
        "Appendix - Proforma adjustments",
        "Appendix - Non-recurring spend"
    ]
    for title in titles:
        if title in section:
            blocks[title] = section.split(title)[-1].strip()
    return blocks


def parse_financial_table(raw_block: str) -> pd.DataFrame:
    lines = [line.strip() for line in raw_block.splitlines() if line.strip()]
    header_lines = []
    data_lines = []

    for line in lines:
        if re.search(r"Feb-\d{2}", line) or "Actual" in line:
            header_lines.append(line)
        else:
            data_lines.append(line)

    # Simplify headers: ['Name', 'Feb-25 Actual', 'Feb-25 Budget', 'Feb-24 Prior', 'Var Budget', 'Var YoY']
    header_combined = ' '.join(header_lines).replace("£", "").strip()
    columns = re.split(r'\s{2,}', header_combined)
    columns = ['Line Item'] + columns[1:]  # Ensure leading label column

    # Process data lines
    data = []
    for line in data_lines:
        parts = re.split(r'\s{2,}', line)
        if len(parts) >= 2:
            row = [parts[0]] + parts[1:]
            while len(row) < len(columns):
                row.append(None)
            data.append(row)

    df = pd.DataFrame(data, columns=columns[:len(data[0])])
    return df


def save_section_to_csv(section_title, df: pd.DataFrame, out_dir="output/csv"):
    os.makedirs(out_dir, exist_ok=True)
    filename = section_title.lower().replace(" ", "_").replace("-", "").replace("/", "_") + ".csv"
    df.to_csv(os.path.join(out_dir, filename), index=False)
    print(f"Saved {section_title} to {filename}")


def process_pdf_file(pdf_path: str):
    print(f"Processing: {pdf_path}")
    full_text = extract_text_from_pdf(pdf_path)
    sections = clean_and_split_sections(full_text)

    for section in sections:
        blocks = extract_table_blocks(section)
        for section_title, block in blocks.items():
            df = parse_financial_table(block)
            save_section_to_csv(section_title, df)


if __name__ == "__main__":
    pdf_file = Path("data/Wilson Group Management Report Finance Appendix Feb 25.pdf")
    if pdf_file.exists():
        process_pdf_file(str(pdf_file))
    else:
        print("PDF file not found. Please place it in the 'data/' directory.")
