import os
import re
import json
import pandas as pd
import pytesseract
from PIL import Image
import pdfplumber
from openpyxl import load_workbook
import numpy as np

RAW_DIR = "data/raw"
PROCESSED_DIR = "data/processed"
os.makedirs(PROCESSED_DIR, exist_ok=True)

def extract_text_from_pdf(pdf_path):
    """Extract raw text from PDF (works for bank, resume, credit report)."""
    text = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text.append(page.extract_text() or "")
    except Exception as e:
        print(f"[WARN] Could not extract from {pdf_path}: {e}")
    return " ".join(text)

def extract_text_from_image(image_path):
    """Extract text from ID images."""
    try:
        return pytesseract.image_to_string(Image.open(image_path))
    except Exception as e:
        print(f"[WARN] Could not OCR {image_path}: {e}")
        return ""

def parse_assets_liabilities(xlsx_path):
    """Parse Excel for assets/liabilities."""
    try:
        df = pd.read_excel(xlsx_path)
        assets = df[df["Type"].str.lower() == "asset"]["Value"].sum()
        liabilities = df[df["Type"].str.lower() == "liability"]["Value"].sum()
        return assets, liabilities
    except Exception as e:
        print(f"[WARN] Could not parse {xlsx_path}: {e}")
        return 0, 0

def extract_numeric(pattern, text, default=0):
    """Utility to extract numbers with regex."""
    match = re.search(pattern, text)
    if match:
        try:
            return float(match.group(1))
        except:
            return default
    return default

def preprocess_applicant(app_id, app_path):
    """Preprocess a single applicant folder into structured dict."""
    record = {"app_id": app_id}
    # Parse files
    for fname in os.listdir(app_path):
        fpath = os.path.join(app_path, fname)
        if "bank_statement" in fname:
            text = extract_text_from_pdf(fpath)
            record["reported_income"] = extract_numeric(r"(\\d{3,5})\\s*A?E?D?", text, default=0)
        elif "emirates_id" in fname:
            text = extract_text_from_image(fpath)
            print(text)
            name_match = re.search(r"Name:\s*(.+)", text, re.MULTILINE)
            dob_match = re.search(r"DOB\s*(\d{4}-\d{2}-\d{2}),?", text)
            record["name"] = name_match.group(1).strip() if name_match else "Unknown"
            record["dob"] = dob_match.group(1) if dob_match else None
            print(record["name"])
            print(record["dob"])

        elif "resume" in fname:
            text = extract_text_from_pdf(fpath)
            # Very basic employment status inference
            record["employment_status"] = "employed" if "experience" in text.lower() else "unemployed"
        elif "credit_report" in fname:
            text = extract_text_from_pdf(fpath)
            record["credit_score"] = extract_numeric(r"(\\d{3})", text, default=600)

        elif "assets_liabilities" in fname:
            assets, liabilities = parse_assets_liabilities(fpath)
            record["assets"] = assets
            record["liabilities"] = liabilities

    # Basic validation & missing value handling
    required_fields = ["name", "dob", "reported_income", "credit_score", "employment_status"]
    for field in required_fields:
        if record.get(field) is None or record.get(field) == "":
            print(f"[CHECK] Missing {field} for {app_id}, filling with defaults.")
            if field == "dob":
                record[field] = "1985-01-01"
            elif field == "name":
                record[field] = f"Unknown_{app_id}"
            elif field == "employment_status":
                record[field] = "unemployed"
            else:
                record[field] = 0

    # Derived metrics
    family_size = record.get("family_size", 4) # default to 4
    income = record.get("reported_income", 0)
    record["per_capita_income"] = round(income / max(1, family_size), 2)

    return record

def main():
    all_records = []
    for app_id in os.listdir(RAW_DIR):
        app_path = os.path.join(RAW_DIR, app_id)
        if os.path.isdir(app_path):
            print(f"Processing {app_id} ...")
            record = preprocess_applicant(app_id, app_path)
            clean_record = {
                k: (int(v) if isinstance(v,(np.int64, np.int32)) else float(v) if isinstance(v,(np.float64, np.float32)) else str(v) if isinstance (v,(pd.Timestamp,)) else v)
                for k,v in record.items()
            }
            all_records.append(record)

            # Save per-app JSON
            with open(os.path.join(PROCESSED_DIR, f"{app_id}.json"), "w") as f:
                json.dump(clean_record, f, indent=2)

    # Save all to CSV
    df = pd.DataFrame(all_records)
    df.to_csv(os.path.join(PROCESSED_DIR, "applications.csv"), index=False)
    print(f"Processed {len(all_records)} applicants. Saved to data/processed/")

if __name__ == "__main__":
    main()
