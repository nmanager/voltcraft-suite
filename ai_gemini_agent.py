#!/usr/bin/env python3
import os
import sys
import json
import subprocess
import sqlite3
from datetime import datetime

# Load Gemini API Key from file if exists
ENV_FILE = os.path.expanduser("~/ai-workspace/.gemini_env")
if os.path.exists(ENV_FILE):
    with open(ENV_FILE, "r") as f:
        for line in f:
            if "GEMINI_API_KEY=" in line:
                val = line.split("=", 1)[1].strip().strip('"').strip("'")
                os.environ["GEMINI_API_KEY"] = val

API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    print("❌ GEMINI_API_KEY is not set!")
    sys.exit(1)

from google import genai
from google.genai import types

def run_ai_growth():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    calcs_path = os.path.join(base_dir, "calculators.json")
    
    with open(calcs_path, "r", encoding="utf-8") as f:
        existing_calcs = json.load(f)
        
    existing_ids = [c["id"] for c in existing_calcs]
    existing_names = [c["name"] for c in existing_calcs]

    print(f"🤖 Connecting to Google Gemini API (Existing tools: {len(existing_ids)})...")
    client = genai.Client(api_key=API_KEY)

    prompt = f"""You are an Autonomous Electrical & Electronics Engineering AI Agent working on VoltCraft (https://voltcraft.pages.dev).
Existing calculators are:
{json.dumps(existing_names, indent=2)}

Your Goal:
Invent 1 BRAND NEW, mathematically verified, high-demand electronics or engineering calculator that is NOT in the list above.
Respond with ONLY valid JSON (no markdown formatting, no code fences):
{{
  "id": "kebab-case-slug",
  "name": "Full Tool Name Calculator",
  "category": "Basic Electrical",
  "affiliate_category": "resistor",
  "meta_title": "SEO Title (60-70 chars) - Key Benefit",
  "meta_desc": "SEO Description (140-160 chars)",
  "summary": "1-2 sentence compelling summary of what problem it solves",
  "inputs": [
    {{"name": "voltage", "label": "Voltage", "default": 12, "unit": "V", "min": 0.1, "max": 1000, "step": 0.1}}
  ],
  "outputs": [
    {{"name": "power", "label": "Power Output", "unit": "W", "formula": "Voltage * Current"}}
  ],
  "formula_latex": "P = V \\times I",
  "faqs": [
    {{"q": "Technical Question 1?", "a": "Precise answer."}},
    {{"q": "Technical Question 2?", "a": "Precise answer."}}
  ],
  "social_promo": "Engaging technical tweet highlighting why engineers need this tool #Electronics #Engineering #Makers"
}}"""

    model_names = ['gemini-3.1-flash-lite', 'gemini-flash-latest', 'gemini-3.8-flash']
    response = None
    used_model = None

    for m in model_names:
        try:
            print(f"Generating new tool using model {m}...")
            response = client.models.generate_content(
                model=m,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.7
                )
            )
            used_model = m
            break
        except Exception as e:
            print(f"Model {m} failed: {e}")

    if not response:
        print("All models failed to generate.")
        sys.exit(1)

    raw_text = response.text.strip()
    try:
        new_tool = json.loads(raw_text)
    except Exception as e:
        print(f"Failed to parse Gemini response: {e}\nRaw output:\n{raw_text}")
        sys.exit(1)

    print(f"✨ Gemini ({used_model}) invented: {new_tool['name']} ({new_tool['id']})")
    
    # Check if duplicate
    if new_tool["id"] in existing_ids:
        print(f"Tool {new_tool['id']} already exists, skipping.")
        return

    # Append to calculators.json
    existing_calcs.append(new_tool)
    with open(calcs_path, "w", encoding="utf-8") as f:
        json.dump(existing_calcs, f, indent=2)

    # Rebuild static site
    print("🔨 Rebuilding static pages & sitemap.xml...")
    build_script = os.path.join(base_dir, "build.py")
    subprocess.run(["python3", build_script], check=True)

    # Save social promotion
    social_dir = os.path.expanduser("~/ai-workspace/data/social_queue")
    os.makedirs(social_dir, exist_ok=True)
    today_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    promo_file = os.path.join(social_dir, f"gemini_promo_{today_str}.md")
    
    promo_content = f"""# 🤖 Gemini AI ({used_model}) Generated Social Promo - {datetime.now().strftime('%Y-%m-%d')}
## ⚡ {new_tool['name']}
- **Live Tool:** https://voltcraft.pages.dev/calculators/{new_tool['id']}.html
- **Category:** {new_tool['category']}
- **Formula:** `{new_tool.get('formula_latex', '')}`

### Social Copy (X / Reddit / LinkedIn):
{new_tool.get('social_promo', '')}
https://voltcraft.pages.dev/calculators/{new_tool['id']}.html
"""
    with open(promo_file, "w", encoding="utf-8") as f:
        f.write(promo_content)
    print(f"📢 Social promo written to: {promo_file}")

    # Deploy to Cloudflare Pages & Git Push
    print("🚀 Deploying updates to Cloudflare Pages & GitHub...")
    deploy_script = os.path.join(base_dir, "deploy.sh")
    if os.path.exists(deploy_script):
        subprocess.run(["bash", deploy_script], check=False)

    # Log to SQLite agent_memory.db
    db_path = os.path.expanduser("~/ai-workspace/data/agent_memory.db")
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            cur.execute("""
            INSERT INTO tasks (task_name, category, status, details, result)
            VALUES (?, ?, ?, ?, ?)
            """, (
                "gemini_autonomous_growth",
                "AI Agent / Programmatic Growth",
                "COMPLETED",
                f"Gemini ({used_model}) invented: {new_tool['name']} ({new_tool['id']})",
                f"Total calculators now: {len(existing_calcs)}. Deployed to https://voltcraft.pages.dev/calculators/{new_tool['id']}.html"
            ))
            conn.commit()
            conn.close()
            print("💾 Task recorded in agent_memory.db")
        except Exception as e:
            print("DB notice:", e)

    print("\n🎉 Gemini Autonomous Agent run finished successfully!")

if __name__ == "__main__":
    run_ai_growth()
