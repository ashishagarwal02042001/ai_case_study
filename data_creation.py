from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
from PIL import Image, ImageDraw, ImageFont
import pandas as pd

# Creation of Bank Statements for user app_001
os.makedirs("data/raw/app_001", exist_ok=True)
c = canvas.Canvas('data/raw/app_001/bank_statements.pdf', pagesize=letter)
c.setFont("Helvetica", 12)
c.drawString(100, 750, "Bank Statement - Account: 123456789")
c.drawString(100, 730, "Date: 2025-10-10 | Description: Salary Deposit | Amount: 5000 AED")
c.drawString(100, 710, "Date: 2025-10-08 | Description: Rent Payment | Amount: -2000 AED")
c.drawString(100, 690, "Closing Balance: 3000 AED")
c.save()

# Creation of Emirates ID for same user
img = Image.new("RGB", (600,300), color = "White")
draw = ImageDraw.Draw(img)
draw.text((50,50), "Emirates ID\nName: Ashish Agarwal\nDOB: 1980-01-01\nID: E1234567", fill = "black")
img.save("data/raw/app_001/emirates_id.jpg")

# Creation of Resume for same user
c = canvas.Canvas("data/raw/app_001/resume.pdf", pagesize=letter)
c.setFont("Helvetica-Bold", 14)
c.drawString(100, 750, "Resume - John Doe")
c.setFont("Helvetica", 12)
c.drawString(100, 730, "Software Engineer, 5 years experience at TechCorp")
c.drawString(100, 710, "Skills: Python, SQL, Data Analysis")
c.drawString(100, 690, "Education: B.Sc. Computer Science")
c.save()

# Creation of Credit report for same user
c = canvas.Canvas("data/raw/app_001/credit_report.pdf", pagesize=letter)
c.setFont("Helvetica", 12)
c.drawString(100, 750, "Credit Report - John Doe")
c.drawString(100, 730, "Credit Score: 580")
c.drawString(100, 710, "Outstanding Loans: 10,000 AED")
c.drawString(100, 690, "Status: Fair")
c.save()

# Creation of Asset for same user
data = {"Category": ["Cash", "Car", "House Loan", "Credit Card"],
"Type": ["Asset", "Asset", "Liability", "Liability"],
"Value": [5000, 20000, 15000, 5000]
}
df = pd.DataFrame(data)
df.to_excel("data/raw/app_001/assets_liabilities.xlsx", index=False)


# User app_002
os.makedirs("data/raw/app_002", exist_ok=True)
# Bank Statement
c = canvas.Canvas("data/raw/app_002/bank_statement.pdf", pagesize=letter)
c.drawString(100, 750, "Bank Statement - Account: 987654321")
c.drawString(100, 730, "Date: 2025-01-01 | Salary Deposit | 7000 AED")
c.drawString(100, 710, "Date: 2025-01-05 | Loan EMI       | -2500 AED")
c.drawString(100, 690, "Closing Balance: 4500 AED")
c.save()

# Emirates ID (image)
img = Image.new("RGB", (600, 300), "white")
draw = ImageDraw.Draw(img)
draw.text((50, 50), "Emirates ID\nName: Aisha Khan\nDOB: 1990-05-10\nID: E7654321", fill="black")
img.save("data/raw/app_002/emirates_id.jpg")

# Resume
c = canvas.Canvas("data/raw/app_002/resume.pdf", pagesize=letter)
c.drawString(100, 750, "Resume - Aisha Khan")
c.drawString(100, 730, "Financial Analyst, 7 years experience at GulfFinance")
c.drawString(100, 710, "Skills: Finance, Risk Analysis, Excel, SQL")
c.save()

# Credit Report
c = canvas.Canvas("data/raw/app_002/credit_report.pdf", pagesize=letter)
c.drawString(100, 750, "Credit Report - Aisha Khan")
c.drawString(100, 730, "Credit Score: 720")
c.drawString(100, 710, "Outstanding Loans: 5000 AED")
c.drawString(100, 690, "Status: Good")
c.save()

# Assets & Liabilities Excel
df = pd.DataFrame({
"Category": ["Cash", "Investments", "Home Loan"],
"Type": ["Asset", "Asset", "Liability"],
"Value": [15000, 20000, 10000]
})
df.to_excel("data/raw/app_002/assets_liabilities.xlsx", index=False)


# User app_003
os.makedirs("data/raw/app_003", exist_ok=True)
# Bank Statement
c = canvas.Canvas("data/raw/app_003/bank_statement.pdf", pagesize=letter)
c.drawString(100, 750, "Bank Statement - Account: 555888999")
c.drawString(100, 730, "Date: 2025-01-02 | Business Income | 4000 AED")
c.drawString(100, 710, "Date: 2025-01-06 | Utilities       | -2000 AED")
c.drawString(100, 690, "Closing Balance: 2000 AED")
c.save()

# Emirates ID
img = Image.new("RGB", (600, 300), "white")
draw = ImageDraw.Draw(img)
draw.text((50, 50), "Emirates ID\nName: Omar Ali\nDOB: 1975-09-22\nID: E5558889", fill="black")
img.save("data/raw/app_003/emirates_id.jpg")

# Resume
c = canvas.Canvas("data/raw/app_003/resume.pdf", pagesize=letter)
c.drawString(100, 750, "Resume - Omar Ali")
c.drawString(100, 730, "Small Business Owner, 15 years experience")
c.drawString(100, 710, "Skills: Management, Sales, Negotiation")
c.save()

# Credit Report
c = canvas.Canvas("data/raw/app_003/credit_report.pdf", pagesize=letter)
c.drawString(100, 750, "Credit Report - Omar Ali")
c.drawString(100, 730, "Credit Score: 640")
c.drawString(100, 710, "Outstanding Loans: 7000 AED")
c.drawString(100, 690, "Status: Average")
c.save()

# Assets & Liabilities
df = pd.DataFrame({
"Category": ["Cash", "Shop Inventory", "Business Loan", "Car Loan"],
"Type": ["Asset", "Asset", "Liability", "Liability"],
"Value": [8000, 5000, 3000, 2000]
})
df.to_excel("data/raw/app_003/assets_liabilities.xlsx", index=False)