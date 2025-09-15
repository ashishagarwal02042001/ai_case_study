import joblib
import os
import re
import json
import numpy as np
import pandas as pd
import pytesseract
import pdfplumber
from PIL import Image
from pathlib import Path
from typing import Tuple, List, Dict
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

MODEL_PATH = os.getenv("ELIGIBILITY_MODEL_PATH", 'models/eligibility_v1.joblib')

class DataExtractionAgent:
    def __init__(self):
        pass

    def _extract_text_from_pdf(self, file_path: str) -> str:
        text = []
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text.append(page.extract_text() or "")
        except Exception as e:
            print(f"[WARN] Could not extract text from PDF {file_path}: {e}")
        return " ".join(text)

    def _extract_text_from_image(self, file_path: str) -> str:
        try:
            return pytesseract.image_to_string(Image.open(file_path))
        except Exception as e:
            print(f"[WARN] Could not OCR {file_path}: {e}")
            return ""

    def _parse_assets_liabilities(self, file_path: str) -> tuple:
        try:
            df = pd.read_excel(file_path)
            assets = df[df["Type"].str.lower() == "asset"]["Value"].sum()
            liabilities = df[df["Type"].str.lower() == "liability"]["Value"].sum()
            return float(assets), float(liabilities)
        except Exception as e:
            print(f"[WARN] Could not parse {file_path}: {e}")
            return 0.0, 0.0

    def _extract_name_dob_from_text(self, text: str) -> tuple:
        name = None
        dob = None
        name_match = re.search(r"Name[: ]*\s*([A-Za-z,\-]+)", text, re.IGNORECASE)
        dob_match = re.search(r"DOB[: ]*\s*(\d{2,4}[-/]\d{2}[-/]\d{2,4})", text, re.IGNORECASE)
        if name_match:
            name = name_match.group(1).strip()
        if dob_match:
            dob = dob_match.group(1)
        return name, dob

    # def _extract_income_from_bank_statement(self, text: str) -> float:
    #     print(text)
    #     match = re.search(r"Salary\s+Deposit\s+([\d,]+)", text, re.IGNORECASE)
    #     print(match)
    #     if match:
    #         return float(match.group(1).replace(",",""))
    #     numbers = re.findall(r"\b\d+(?:\.\d+)?\b", text)
    #     if numbers:
    #         positive_numbers = [float(num) for num in numbers if not text.find(f"-{num}")!=-1]
    #         print(positive_numbers)
    #         if positive_numbers:
    #             return max(positive_numbers)
    #     return 0.0
    def _extract_income_from_bank_statement(self, text: str) -> float:
        # print("Input text:\n", text)
        model = genai.GenerativeModel("gemini-2.0-flash")
        prompt = f"""You are an information extraction assistant. From the following bank statement text, extract the salary deposit amount (the credited salary). If no salary deposit is found, return 0. Text:{text}"""
        response = model.generate_content(prompt)
        try:
            extracted = response.text.strip()
            salary = float("".join(ch for ch in extracted if ch.isdigit() or ch == "."))
            return salary
        except Exception as e:
            print("Parsing error:", e)
            return 0.0

    def _extract_credit_score(self, text: str) -> int:
        match = re.search(r"Credit\s*Score:\s*(\d{3})", text, re.IGNORECASE)
        if match:
            return int(match.group(1))
        return 600

    def _infer_employment_status(self, text: str) -> str:
        if "experience" in text.lower() or "engineer" in text.lower() or "analyst" in text.lower():
            return "employed"
        if "self-employed" in text.lower() or "business" in text.lower():
            return "self-employed"
        return "unemployed"

    def extract(self, application: dict) -> dict:
        parsed = {"app_form": {}, "documents": []}
        for f in application.get("files", []):
            doc_info = {"file_path": f, "parsed_text": ""}
            if f.lower().endswith(".pdf"):
                text = self._extract_text_from_pdf(f)
                # print(text)
                doc_info["parsed_text"] = text

                if "bank_statement" in f.lower():
                    parsed["app_form"]["reported_income"] = self._extract_income_from_bank_statement(text)

                elif "resume" in f.lower():
                    parsed["app_form"]["employment_status"] = self._infer_employment_status(text)

                elif "credit_report" in f.lower():
                    parsed["app_form"]["credit_score"] = self._extract_credit_score(text)

            elif f.lower().endswith((".jpg", ".jpeg", ".png")):
                text = self._extract_text_from_image(f)
                # print(text)
                doc_info["parsed_text"] = text
                name, dob = self._extract_name_dob_from_text(text)
                if name:
                    parsed["app_form"]["name"] = name
                if dob:
                    parsed["app_form"]["dob"] = dob

            elif f.lower().endswith(".xlsx"):
                assets, liabilities = self._parse_assets_liabilities(f)
                parsed["app_form"]["assets"] = assets
                parsed["app_form"]["liabilities"] = liabilities

            parsed["documents"].append(doc_info)

        parsed["app_form"].setdefault("family_size", 4)
        parsed["app_form"].setdefault("reported_income", 0)
        parsed["app_form"].setdefault("employment_status", "unemployed")
        parsed["app_form"].setdefault("credit_score", 600)
        parsed["app_form"].setdefault("assets", 0)
        parsed["app_form"].setdefault("liabilities", 0)
        # print(parsed)
        return parsed

class ValidationAgent:
    def __init__(self):
        pass

    def validate(self, application: dict, parsed_docs: dict) -> Dict:
        report = {
            "address_match": True,
            "income_match": True,
            "conflicts": [],
            "confidence": 0.95,
        }
        return report

class EligibilityAgent:
    def __init__(self):
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Model not found. Please run Scripts/train_eligibility_model.py to create it.")
        self.pipeline = joblib.load(MODEL_PATH)
    
    def _build_feature_vector(self, application:dict, parsed_docs: dict):
        age = application.get('age') or self._approximate_age_from_dob(application.get('dob'))
        family_size = application.get('family_size', 1)
        monthly_income = application.get('reported_income', 0)
        employment_status = application.get('employment_status') or 'unemployed'
        assets = application.get('assets', 0)
        liabilities = application.get('liabilities', 0)
        credit_score = application.get('credit_score', 600)

        x_row = {
            'age':age,
            'family_size':family_size,
            'monthly_income':monthly_income,
            'employment_status':employment_status,
            'assets':assets,
            'liabilities':liabilities,
            'credit_score':credit_score
        }

        return x_row
    
    def _approximate_age_from_dob(self, dob_str):
        try:
            from datetime import datetime
            if not dob_str:
                return 35
            dob = datetime.strptime(dob_str.split('T')[0],'%Y-%m-%d')
            today = datetime.today()
            return today.year - dob.year - ((today.month, today.day)<(dob.month, dob.day))
        except Exception:
            return 35
        
    def assess(self, application:dict, parsed_docs:dict, validation_report:dict) -> Tuple[str, float, List[str], List[str]]:
        x_row = self._build_feature_vector(application, parsed_docs)
        try:
            import pandas as pd
            x_df = pd.DataFrame([x_row])
        except Exception:
            x_df = [[v for v in x_row.values()]]
        
        proba = None
        try:
            proba = self.pipeline.predict_proba(x_df)
        except Exception:
            pass

        pred = self.pipeline.predict(x_df)[0]
        unique_classes = None
        if proba is not None:
            class_index = list(self.pipeline.classes_).index(pred)
            score = float(proba[0][class_index])
        else:
            score = 1.0 if pred == 'approve' else 0.5
        # print(pred)
        reasons_map = {
            'approve':['meets_income_threshold', 'low_per_capita_income'],
            'soft-decline':['marginal_income'],
            'reject':['sufficient_income']
        }

        recs_map = {
            'approve':['upskill', 'job_match'],
            'soft-decline':['counseling'],
            'reject':[]
        }

        reasons = reasons_map.get(pred,[])
        recommendations = recs_map.get(pred,[])
        # print(pred, score, reasons, recommendations)
        return pred, score, reasons, recommendations
    

class ExplanationAgent:
    def __init__(self):
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI API Key not found. Set the GOOGLE_API_KEY environment variable.")
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        self.processed_dir = Path("data/saved_applications")

    def _load_app_context(self, app_id:str):
        app_file = self.processed_dir/f"{app_id}.json"
        if app_file.exists():
            with open(app_file) as f:
                data = json.load(f)
            return json.dumps(data, indent=2)
        return ""

    def explain(
        self,
        application: dict,
        parsed_docs: dict,
        validation_report: dict,
        decision: str,
        score: float,
        recommendations: List[str]
    ) -> str:
        prompt = (f"Application {application.get('app_id')} was processed with the following results:\\n\Decision: {decision} (confidence {round(score,2)})\\n\Reasons: {', '.join(recommendations) if recommendations else 'None'}\\n\Validation Report: {validation_report}\\n""\Please explain in simple language what this means for the applicant, including any suggestions to improve their eligibility.\"\n")

        try:
            response = self.model.generate_content(contents=prompt)
            return response.text
        except Exception as e:
            return f'[Error calling LLM: {e}]'

    def answer_query(self, query: str, app_id: str = None) -> str:
        context = self._load_app_context(app_id) if app_id else ""
        prompt = f"You are a social support eligibility assistant. Applicant ID: {app_id or '(unknown)'} Context: {context}\n asks: {query}\\n\ Please answer clearly, referencing what eligibility means and what they can do next."
        
        try:
            response = self.model.generate_content(contents=prompt)
            return response.text
        except Exception as e:
            return f'[Error calling LLM: {e}]'