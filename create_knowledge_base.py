import os

# Create the knowledge_base folder if it doesn't already exist
os.makedirs("knowledge_base", exist_ok=True)

# 1. Company Policies required by the assignment
policies = {
    "shipping_policy.md": """# Shipping Policy
- Standard Shipping: 3-5 business days ($4.99 flat fee, free on orders over $50).
- Express Delivery: 1-2 business days ($14.99).
- Delivery Delays: If tracking does not update for 24 hours past the estimated arrival date, contact customer support to open an investigation.
- Lost or Missing Packages: Must be reported within 14 days of the expected delivery date.""",

    "refund_policy.md": """# Refund and Return Policy
- Return Window: Items can be returned within 30 days of confirmed delivery date.
- Condition: Items must be unused, unworn, and in their original packaging.
- Refund Timeline: Refunds take 5-7 business days to process back to the original payment method after warehouse inspection.
- Damaged / Broken Items: Eligible for an immediate free replacement or full refund upon providing photo evidence.""",

    "account_and_login.md": """# Account & Login Help
- Password Reset: Click the 'Forgot Password' link on the login page; a reset link is emailed and expires in 15 minutes.
- Locked Account: Accounts are locked for 30 minutes after 5 consecutive failed login attempts.
- Security Requirements: Passwords must contain at least 8 characters, 1 number, and 1 special symbol.""",

    "product_faq.md": """# General Product FAQ
- Electronics Warranty: All brand electronics carry a 1-year limited manufacturer warranty covering factory defects.
- Corporate / Bulk Orders: For orders of 50 units or more, please email corporate-sales@store.com.
- Custom Branding: Custom logo printing requires a 500-unit minimum order and requires a 6-week lead time."""
}

for filename, content in policies.items():
    path = os.path.join("knowledge_base", filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip())
    print(f"Created policy doc: {path}")

# 2. Generate a valid sample Product PDF (ApexSound Pulse Pro Wireless Headphones)
pdf_content = b"""%PDF-1.4
1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj
2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj
3 0 obj << /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >> endobj
4 0 obj << /Length 430 >> stream
BT
/F1 16 Tf
50 720 Td (ApexSound Pulse Pro Wireless Headphones - User Manual) Tj
/F1 11 Tf
0 -30 Td (Product Model: AS-PRO-BT2 | Firmware: v3.4.1) Tj
0 -25 Td (1. Bluetooth Pairing: Press and hold the power button for 5 seconds until LED blinks Blue/Red.) Tj
0 -20 Td (2. Hardware Reset: Hold Power and Volume-Down buttons together for 10 seconds to restore factory settings.) Tj
0 -20 Td (3. Battery & Charging: 40 hours battery life. Full charge takes 90 minutes via USB-C.) Tj
0 -20 Td (4. Water Resistance: IPX5 splash-proof. Not submersible in water. Do not swim with headphones.) Tj
0 -20 Td (5. Warranty: 1-Year Limited Warranty covers hardware failure, battery defects, and audio distortion.) Tj
ET
endstream
endobj
5 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj
xref
0 6
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000229 00000 n 
0000000711 00000 n 
trailer << /Size 6 /Root 1 0 R >>
startxref
791
%%EOF"""

pdf_path = os.path.join("knowledge_base", "apexsound_headphones_manual.pdf")
with open(pdf_path, "wb") as f:
    f.write(pdf_content)

print(f"Created product PDF: {pdf_path}")