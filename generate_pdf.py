import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

os.makedirs("knowledge_base", exist_ok=True)
pdf_path = os.path.join("knowledge_base", "apexsound_headphones_manual.pdf")

# Generate standard, 100% valid PDF
c = canvas.Canvas(pdf_path, pagesize=letter)
width, height = letter

# Title
c.setFont("Helvetica-Bold", 16)
c.drawString(50, 740, "ApexSound Pulse Pro Wireless Headphones - User Manual")

# Metadata
c.setFont("Helvetica-Oblique", 10)
c.drawString(50, 715, "Model: AS-PRO-BT2 | Firmware: v3.4.1 | Documentation Version: 1.0")

# Manual Sections
c.setFont("Helvetica-Bold", 12)
c.drawString(50, 680, "1. Bluetooth Pairing")
c.setFont("Helvetica", 10)
c.drawString(50, 665, "To pair, press and hold the Power button for 5 seconds until the LED flashes blue and red.")
c.drawString(50, 650, "Select 'ApexSound Pulse Pro' from your device's Bluetooth settings menu.")

c.setFont("Helvetica-Bold", 12)
c.drawString(50, 620, "2. Factory Reset Procedure")
c.setFont("Helvetica", 10)
c.drawString(50, 605, "Hold the Power button and Volume-Down button simultaneously for 10 seconds.")
c.drawString(50, 590, "The LED will blink red three times, restoring all original factory default settings.")

c.setFont("Helvetica-Bold", 12)
c.drawString(50, 560, "3. Battery & Fast Charging")
c.setFont("Helvetica", 10)
c.drawString(50, 545, "Total battery life provides up to 40 hours of playback at 50% volume.")
c.drawString(50, 530, "A full charge takes 90 minutes via USB-C. A 10-minute quick charge offers 4 hours of playtime.")

c.setFont("Helvetica-Bold", 12)
c.drawString(50, 500, "4. Water Resistance Guidelines")
c.setFont("Helvetica", 10)
c.drawString(50, 485, "The headphones are rated IPX5 splash and sweat resistant.")
c.drawString(50, 470, "Do NOT submerge the device in water or wear it while swimming or showering.")

c.setFont("Helvetica-Bold", 12)
c.drawString(50, 440, "5. Warranty Coverage")
c.setFont("Helvetica", 10)
c.drawString(50, 425, "Includes a 1-Year Limited Manufacturer Warranty covering internal hardware defect and battery failure.")
c.drawString(50, 410, "Warranty does not cover accidental drops, unauthorized disassembly, or liquid submersion.")

c.save()
print(f"Successfully generated clean PDF: {pdf_path}")