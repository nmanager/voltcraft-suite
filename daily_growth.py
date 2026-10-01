#!/usr/bin/env python3
import json
import os
import subprocess
import sqlite3
from datetime import datetime

GROWTH_BACKLOG = [
  {
    "id": "capacitor-energy-calculator",
    "name": "Capacitor Stored Energy & Charge Calculator",
    "category": "Basic Electrical",
    "affiliate_category": "resistor",
    "meta_title": "Capacitor Energy Calculator (Joules) - Voltage & Capacitance",
    "meta_desc": "Calculate electrical energy stored in a capacitor in Joules and charge in Coulombs.",
    "summary": "Determine the destructive energy or pulse power capacity stored in high voltage capacitors.",
    "inputs": [
      {"name": "c", "label": "Capacitance (C)", "default": 1000, "unit": "μF", "min": 0.1, "max": 100000, "step": 10},
      {"name": "v", "label": "Voltage across Capacitor", "default": 24, "unit": "V", "min": 0.1, "max": 1000, "step": 1}
    ],
    "outputs": [
      {"name": "energy_joules", "label": "Stored Energy", "unit": "Joules (J)", "formula": "0.5 * (C * 1e-6) * V^2"},
      {"name": "charge_coulombs", "label": "Stored Charge", "unit": "Coulombs (C)", "formula": "(C * 1e-6) * V"}
    ],
    "formula_latex": "E = \\frac{1}{2} C V^2 \\quad \\& \\quad Q = C V",
    "faqs": [
      {"q": "Can a charged capacitor be lethal?", "a": "Yes. Stored energy exceeding 10 Joules can deliver painful or dangerous electric shocks. Always install bleeder resistors."}
    ]
  },
  {
    "id": "opamp-inverting-gain-calculator",
    "name": "Op-Amp Inverting Amplifier Gain Calculator",
    "category": "Digital & PCB",
    "affiliate_category": "resistor",
    "meta_title": "Inverting Op-Amp Gain & Output Voltage Calculator",
    "meta_desc": "Calculate voltage gain (Av) and output voltage for inverting operational amplifier circuits.",
    "summary": "Design analog signal conditioning and sensor preamplifiers with exact resistor ratios.",
    "inputs": [
      {"name": "vin", "label": "Input Voltage (Vin)", "default": 0.5, "unit": "V", "min": -15, "max": 15, "step": 0.1},
      {"name": "rin", "label": "Input Resistor (Rin)", "default": 10000, "unit": "Ω", "min": 100, "max": 10000000, "step": 1000},
      {"name": "rf", "label": "Feedback Resistor (Rf)", "default": 47000, "unit": "Ω", "min": 100, "max": 10000000, "step": 1000}
    ],
    "outputs": [
      {"name": "gain", "label": "Voltage Gain (Av)", "unit": "V/V", "formula": "- (Rf / Rin)"},
      {"name": "vout", "label": "Output Voltage (Vout)", "unit": "V", "formula": "- Vin * (Rf / Rin)"}
    ],
    "formula_latex": "A_v = -\\frac{R_f}{R_{in}} \\quad \\& \\quad V_{out} = -V_{in} \\times \\frac{R_f}{R_{in}}",
    "faqs": [
      {"q": "Why is the gain negative?", "a": "The inverting amplifier introduces a 180° phase inversion between the input signal and output signal."}
    ]
  },
  {
    "id": "quarter-wave-antenna-calculator",
    "name": "Quarter-Wave Whip Antenna Length Calculator",
    "category": "RF & Audio",
    "affiliate_category": "measurement",
    "meta_title": "Quarter-Wave Whip Antenna Length Calculator - Frequency to Length",
    "meta_desc": "Compute physical length of 1/4 wavelength whip antennas for 433MHz, 868MHz, 915MHz, Wi-Fi and VHF/UHF.",
    "summary": "Maximize RF transmission range for LoRa, Sub-GHz, and wireless IoT nodes.",
    "inputs": [
      {"name": "freq_mhz", "label": "Carrier Frequency", "default": 433.92, "unit": "MHz", "min": 1, "max": 6000, "step": 0.5},
      {"name": "vf", "label": "Velocity Factor (k)", "default": 0.95, "unit": "factor", "min": 0.5, "max": 1.0, "step": 0.01}
    ],
    "outputs": [
      {"name": "length_cm", "label": "Antenna Length", "unit": "cm", "formula": "(75 / Freq) * Vf * 100"},
      {"name": "length_inches", "label": "Antenna Length", "unit": "inches", "formula": "((75 / Freq) * Vf * 100) / 2.54"}
    ],
    "formula_latex": "L = \\frac{c \\times k}{4 \\times f}",
    "faqs": [
      {"q": "What is velocity factor?", "a": "Signals travel ~5% slower through metal conductors than in a vacuum, requiring a typical velocity factor of 0.95."}
    ]
  },
  {
    "id": "battery-c-rate-calculator",
    "name": "Battery C-Rate & Maximum Discharge Current Calculator",
    "category": "Power & Battery",
    "affiliate_category": "battery",
    "meta_title": "Battery C-Rate Calculator - Continuous & Peak Discharge Amps",
    "meta_desc": "Calculate maximum continuous and burst discharge current in Amperes from battery capacity and C-rating.",
    "summary": "Ensure LiPo and LiFePO4 batteries can safely deliver power without thermal runaway.",
    "inputs": [
      {"name": "capacity_mah", "label": "Pack Capacity", "default": 2200, "unit": "mAh", "min": 100, "max": 100000, "step": 50},
      {"name": "c_rating", "label": "Continuous C-Rating", "default": 25, "unit": "C", "min": 0.5, "max": 150, "step": 1}
    ],
    "outputs": [
      {"name": "max_amps", "label": "Max Continuous Current", "unit": "A", "formula": "(Capacity / 1000) * C"},
      {"name": "depletion_min", "label": "Full Depletion Time", "unit": "minutes", "formula": "60 / C"}
    ],
    "formula_latex": "I_{max} = \\frac{\\text{Capacity}_{mAh}}{1000} \\times C",
    "faqs": [
      {"q": "What does a 25C rating mean?", "a": "A 25C battery can be safely discharged at 25 times its capacity in 1/25th of an hour (2.4 minutes)."}
    ]
  }
]

def run_growth():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    calcs_path = os.path.join(base_dir, "calculators.json")
    
    with open(calcs_path, "r", encoding="utf-8") as f:
        existing = json.load(f)
        
    existing_ids = {c["id"] for c in existing}
    new_candidates = [c for c in GROWTH_BACKLOG if c["id"] not in existing_ids]

    if not new_candidates:
        print("All backlog calculators already deployed.")
        return

    # Pick 2-3 new calculators
    to_add = new_candidates[:3]
    existing.extend(to_add)

    with open(calcs_path, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2)

    # Re-run build.py
    build_script = os.path.join(base_dir, "build.py")
    subprocess.run(["python3", build_script], check=True)

    # Generate social promotion queue
    social_dir = os.path.expanduser("~/ai-workspace/data/social_queue")
    os.makedirs(social_dir, exist_ok=True)
    today_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    promo_file = os.path.join(social_dir, f"promo_{today_str}.md")

    promo_lines = [f"# Automated Social Media Growth Snippets - {datetime.now().strftime('%Y-%m-%d')}\n"]
    for c in to_add:
        snippet = f"""## ⚡ {c['name']}
- **Hook:** Tired of slow, ad-choked calculators for {c['category']}?
- **Solution:** Compute {c['meta_title']} with instant live interactive sliders on VoltCraft.
- **Link:** https://voltcraft.pages.dev/calculators/{c['id']}.html
- **Hashtags:** #Electronics #Engineering #Hardware #Makers #IoT #DIY #OpenSource

---
"""
        promo_lines.append(snippet)

    with open(promo_file, "w", encoding="utf-8") as f:
        f.write("".join(promo_lines))

    # Log to SQLite agent_memory.db
    db_path = os.path.expanduser("~/ai-workspace/data/agent_memory.db")
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            cur.execute("INSERT INTO tasks (task_name, category, status, details, result) VALUES (?, ?, ?, ?, ?)",
                        ("daily_growth_run", "Programmatic SEO", "COMPLETED",
                         f"Added {len(to_add)} new calculators: {', '.join([c['name'] for c in to_add])}",
                         f"Total calculators now: {len(existing)}. Promo generated at {promo_file}"))
            conn.commit()
            conn.close()
        except Exception as e:
            print("DB log notice:", e)

    print(f"Growth loop succeeded: Added {len(to_add)} tools. Social snippets saved to {promo_file}")

if __name__ == "__main__":
    run_growth()
