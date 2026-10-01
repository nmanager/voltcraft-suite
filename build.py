#!/usr/bin/env python3
import json
import os
import html
from datetime import datetime

BASE_URL = "https://voltcraft.pages.dev"

def load_json(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def generate_sitemap(calculators, out_dir):
    today = datetime.now().strftime("%Y-%m-%d")
    urls = [f"""  <url>
    <loc>{BASE_URL}/</loc>
    <lastmod>{today}</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>"""]
    
    for c in calculators:
        urls.append(f"""  <url>
    <loc>{BASE_URL}/calculators/{c['id']}.html</loc>
    <lastmod>{today}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>""")
        
    sitemap_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{chr(10).join(urls)}
</urlset>"""

    with open(os.path.join(out_dir, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(sitemap_content)
    print("sitemap.xml generated.")

def generate_robots(out_dir):
    robots_content = f"""User-agent: *
Allow: /
Sitemap: {BASE_URL}/sitemap.xml
"""
    with open(os.path.join(out_dir, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(robots_content)
    print("robots.txt generated.")

def build_index_html(calculators, monetization, out_dir):
    cards_html = []
    categories = sorted(list(set(c["category"] for c in calculators)))
    chips_html = ['<button class="chip active" data-category="all">All Tools</button>']
    for cat in categories:
        chips_html.append(f'<button class="chip" data-category="{html.escape(cat)}">{html.escape(cat)}</button>')

    for c in calculators:
        card = f"""
      <a href="calculators/{c['id']}.html" class="calc-card" data-title="{html.escape(c['name'])}" data-category="{html.escape(c['category'])}" data-desc="{html.escape(c['summary'])}">
        <div class="calc-card-cat">{html.escape(c['category'])}</div>
        <h3>{html.escape(c['name'])}</h3>
        <p>{html.escape(c['summary'])}</p>
        <div class="calc-card-footer">
          <span>Open Interactive Tool</span>
          <span>⚡ &rarr;</span>
        </div>
      </a>"""
        cards_html.append(card)

    schema_json = {
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": "VoltCraft - Smart Engineering & Electronics Calculators",
        "applicationCategory": "DeveloperApplication",
        "operatingSystem": "All",
        "offers": {
            "@type": "Offer",
            "price": "0",
            "priceCurrency": "USD"
        },
        "description": "Interactive online suite of 40+ free electronics, hardware design, and electrical engineering calculators."
    }

    coffee_url = monetization["monetization"]["buy_me_a_coffee"]["url"]

    index_html = f"""<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>VoltCraft ⚡ Free Engineering & Electronics Calculator Suite</title>
  <meta name="description" content="Free, 100% client-side engineering, PCB, and electronics calculators. Ohm's Law, LED Resistors, Voltage Dividers, 555 Timers, Battery Life & RF tools.">
  <meta property="og:title" content="VoltCraft - Smart Electronics & Hardware Calculators">
  <meta property="og:description" content="Instant, accurate, zero-bloat engineering calculations running 100% in your browser.">
  <meta property="og:type" content="website">
  <meta property="og:url" content="{BASE_URL}/">
  <link rel="canonical" href="{BASE_URL}/">
  <link rel="stylesheet" href="style.css">
  <script type="application/ld+json">
    {json.dumps(schema_json, indent=2)}
  </script>
</head>
<body>
  <header>
    <div class="container nav-wrapper">
      <a href="index.html" class="brand">
        <div class="brand-icon">⚡</div>
        <span>VoltCraft</span>
      </a>
      <div class="nav-actions">
        <button class="theme-toggle" id="themeToggle" title="Toggle theme">☀️</button>
        <a href="{coffee_url}" target="_blank" rel="noopener" class="btn-coffee">☕ Buy Me a Coffee</a>
      </div>
    </div>
  </header>

  <main class="container">
    <section class="hero">
      <div class="badge">🚀 100% Client-Side & Free Forever</div>
      <h1>The Zero-BS <span>Engineering & Electronics</span> Calculator Suite</h1>
      <p>Precision tools for hardware makers, engineers, and students. Instant formulas, zero intrusive ads, zero tracking.</p>

      <div class="search-box-wrapper">
        <span class="search-icon">🔍</span>
        <input type="text" id="calcSearch" class="search-input" placeholder="Search calculators (e.g. resistor, 555 timer, pcb trace, battery)...">
      </div>

      <div class="filter-chips">
        {"".join(chips_html)}
      </div>
    </section>

    <!-- Featured Live Interactive Quick Tool -->
    <section class="featured-calculator">
      <div class="calc-header">
        <div>
          <h2 style="font-size: 1.4rem; font-weight: 700;">⚡ Quick Ohm's Law & Power Solver</h2>
          <p style="color: var(--text-muted); font-size: 0.9rem;">Adjust sliders or numbers to see instant mathematical convergence</p>
        </div>
        <span class="badge" style="margin-bottom:0">Live Interactive</span>
      </div>

      <div class="calc-grid">
        <div class="inputs-col">
          <div class="input-group">
            <div class="input-label-row">
              <label for="quick_v">Voltage (V)</label>
              <span id="lbl_v" style="color: var(--accent-cyan); font-weight:700;">Volts</span>
            </div>
            <div class="input-control-row">
              <input type="number" id="quick_v" class="num-input" value="12" step="0.5" min="0.1" max="1000">
              <input type="range" id="quick_v_slider" class="range-slider" value="12" step="0.5" min="0.1" max="100">
            </div>
          </div>

          <div class="input-group">
            <div class="input-label-row">
              <label for="quick_i">Current (I)</label>
              <span id="lbl_i" style="color: var(--accent-cyan); font-weight:700;">Amps</span>
            </div>
            <div class="input-control-row">
              <input type="number" id="quick_i" class="num-input" value="2" step="0.1" min="0.01" max="100">
              <input type="range" id="quick_i_slider" class="range-slider" value="2" step="0.1" min="0.01" max="20">
            </div>
          </div>
        </div>

        <div class="results-col">
          <div class="result-card">
            <div class="result-metric">
              <div class="result-label">Calculated Resistance (R = V / I)</div>
              <div class="result-val" id="quick_out_r">6.00 Ω</div>
            </div>
            <div class="result-metric" style="margin-bottom:0">
              <div class="result-label">Dissipated Power (P = V × I)</div>
              <div class="result-val" id="quick_out_p" style="color: var(--accent-amber)">24.00 W</div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Calculator Directory Grid -->
    <div class="section-title">
      <h2>All Precision Calculators</h2>
      <span style="font-size: 0.95rem; color: var(--text-muted); font-weight: normal;">{len(calculators)} verified tools</span>
    </div>

    <div class="cards-grid">
      {"".join(cards_html)}
    </div>

    <!-- Monetization / Partner Banner -->
    <div class="affiliate-section">
      <div class="affiliate-content">
        <h4>🛠️ Need High-Precision Components or PCB Fabrication?</h4>
        <p>Order high quality prototype PCBs for $2 with fast global shipping, SMT assembly from $8, or explore verified component kits.</p>
      </div>
      <a href="https://jlcpcb.com/?from=CDVDWKJNX" target="_blank" rel="noopener" class="btn-affiliate">Order Prototype PCBs ($2) &rarr;</a>
    </div>
  </main>

  <footer>
    <div class="container">
      <div class="footer-links">
        <a href="index.html">Home</a>
        <a href="sitemap.xml">Sitemap</a>
        <a href="{coffee_url}" target="_blank" rel="noopener">Support</a>
      </div>
      <p>&copy; {datetime.now().year} VoltCraft. Open-source, zero-tracking, ultra-fast engineering calculations.</p>
    </div>
  </footer>

  <script src="app.js"></script>
</body>
</html>"""

    with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(index_html)
    print("index.html generated successfully.")

def build_programmatic_calculator_pages(calculators, monetization, out_dir):
    calc_dir = os.path.join(out_dir, "calculators")
    os.makedirs(calc_dir, exist_ok=True)
    coffee_url = monetization["monetization"]["buy_me_a_coffee"]["url"]
    affiliates = monetization["monetization"]["contextual_affiliates"]

    for c in calculators:
        calc_id = c["id"]
        aff = next((a for a in affiliates if a["category"] == c.get("affiliate_category")), affiliates[0])

        # Dynamic FAQ Schema
        faq_entities = []
        faq_html_list = []
        for faq in c.get("faqs", []):
            faq_entities.append({
                "@type": "Question",
                "name": faq["q"],
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": faq["a"]
                }
            })
            faq_html_list.append(f"""
          <div style="margin-bottom: 1.25rem;">
            <h4 style="font-size: 1.05rem; font-weight: 700; margin-bottom: 0.35rem; color: var(--text-main);">Q: {html.escape(faq['q'])}</h4>
            <p style="color: var(--text-muted); font-size: 0.95rem;">{html.escape(faq['a'])}</p>
          </div>""")

        schema_json = {
            "@context": "https://schema.org",
            "@graph": [
                {
                    "@type": "SoftwareApplication",
                    "name": c["name"],
                    "applicationCategory": "DeveloperApplication",
                    "operatingSystem": "All",
                    "offers": {
                        "@type": "Offer",
                        "price": "0",
                        "priceCurrency": "USD"
                    },
                    "description": c["meta_desc"]
                },
                {
                    "@type": "FAQPage",
                    "mainEntity": faq_entities
                }
            ]
        }

        # Build dynamic inputs HTML
        inputs_html = []
        calc_js_lines = []
        for inp in c["inputs"]:
            name = inp["name"]
            label = inp["label"]
            unit = inp.get("unit", "")
            dval = inp.get("default", 0)
            step = inp.get("step", 1)
            min_v = inp.get("min", 0)
            max_v = inp.get("max", 1000)

            if inp.get("type") == "text":
                inputs_html.append(f"""
              <div class="input-group">
                <div class="input-label-row">
                  <label for="inp_{name}">{html.escape(label)}</label>
                </div>
                <input type="text" id="inp_{name}" class="num-input" value="{dval}" style="width:100%;">
              </div>""")
                calc_js_lines.append(f"const {name} = document.getElementById('inp_{name}').value.trim();")
            else:
                inputs_html.append(f"""
              <div class="input-group">
                <div class="input-label-row">
                  <label for="inp_{name}">{html.escape(label)}</label>
                  <span style="color: var(--accent-cyan); font-weight:700;">{unit}</span>
                </div>
                <div class="input-control-row">
                  <input type="number" id="inp_{name}" class="num-input" value="{dval}" step="{step}" min="{min_v}" max="{max_v}">
                  <input type="range" id="slider_{name}" class="range-slider" value="{dval}" step="{step}" min="{min_v}" max="{max_v}">
                </div>
              </div>""")
                calc_js_lines.append(f"const {name} = parseFloat(document.getElementById('inp_{name}').value) || 0;")

        # Build dynamic outputs HTML
        outputs_html = []
        for out in c["outputs"]:
            oname = out["name"]
            olabel = out["label"]
            ounit = out["unit"]
            outputs_html.append(f"""
              <div class="result-metric">
                <div class="result-label">{html.escape(olabel)} ({ounit})</div>
                <div class="result-val" id="out_{oname}">—</div>
              </div>""")

        page_html = f"""<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(c['meta_title'])} | VoltCraft</title>
  <meta name="description" content="{html.escape(c['meta_desc'])}">
  <meta property="og:title" content="{html.escape(c['meta_title'])}">
  <meta property="og:description" content="{html.escape(c['meta_desc'])}">
  <meta property="og:type" content="article">
  <meta property="og:url" content="{BASE_URL}/calculators/{calc_id}.html">
  <link rel="canonical" href="{BASE_URL}/calculators/{calc_id}.html">
  <link rel="stylesheet" href="../style.css">
  <script type="application/ld+json">
    {json.dumps(schema_json, indent=2)}
  </script>
</head>
<body>
  <header>
    <div class="container nav-wrapper">
      <a href="../index.html" class="brand">
        <div class="brand-icon">⚡</div>
        <span>VoltCraft</span>
      </a>
      <div class="nav-actions">
        <button class="theme-toggle" id="themeToggle" title="Toggle theme">☀️</button>
        <a href="{coffee_url}" target="_blank" rel="noopener" class="btn-coffee">☕ Buy Me a Coffee</a>
      </div>
    </div>
  </header>

  <main class="container" style="padding-top: 2.5rem;">
    <div style="margin-bottom: 1.5rem;">
      <a href="../index.html" style="color: var(--accent-cyan); text-decoration:none; font-size:0.9rem; font-weight:600;">&larr; Back to All Calculators</a>
    </div>

    <div class="badge">{html.escape(c['category'])}</div>
    <h1 style="font-size: 2.2rem; font-weight: 800; margin-bottom: 0.75rem;">{html.escape(c['name'])}</h1>
    <p style="color: var(--text-muted); font-size: 1.1rem; max-width: 800px; margin-bottom: 2rem;">{html.escape(c['summary'])}</p>

    <div class="featured-calculator" style="margin-bottom: 2.5rem;">
      <div class="calc-grid">
        <div class="inputs-col">
          <h3 style="font-size: 1.15rem; font-weight:700; margin-bottom: 1.25rem;">Input Parameters</h3>
          {"".join(inputs_html)}
        </div>

        <div class="results-col">
          <h3 style="font-size: 1.15rem; font-weight:700; margin-bottom: 1.25rem;">Calculation Results</h3>
          <div class="result-card">
            {"".join(outputs_html)}
            <button onclick="window.triggerProExport()" style="margin-top:1rem; padding:0.6rem 1rem; background:rgba(6,182,212,0.15); border:1px solid var(--accent-cyan); color:var(--accent-cyan); border-radius:var(--radius-md); font-weight:600; cursor:pointer;">
              📄 Export Calculation Report (Pro)
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Contextual Affiliate Recommendation -->
    <div class="affiliate-section" style="margin-bottom: 2.5rem; padding: 1.5rem;">
      <div class="affiliate-content">
        <span class="badge" style="background: rgba(245,158,11,0.2); border-color: var(--accent-amber); color: var(--accent-amber); margin-bottom: 0.5rem;">
          {html.escape(aff['tag'])} ({html.escape(aff['vendor'])})
        </span>
        <h4 style="font-size: 1.15rem; color: var(--text-main);">{html.escape(aff['title'])}</h4>
        <p style="font-size: 0.88rem;">Tested and recommended for reliable hardware prototyping and accurate measurements.</p>
      </div>
      <a href="{aff['url']}" target="_blank" rel="noopener" class="btn-affiliate" style="padding: 0.6rem 1.25rem; font-size: 0.9rem;">View Recommended Part &rarr;</a>
    </div>

    <!-- Formula & Engineering Explanation -->
    <section style="background: var(--bg-card); border: 1px solid var(--border-color); border-radius: var(--radius-lg); padding: 2rem; margin-bottom: 2.5rem;">
      <h3 style="font-size: 1.25rem; font-weight: 700; margin-bottom: 1rem;">Formula & Theory</h3>
      <div style="background: var(--bg-secondary); padding: 1rem; border-radius: var(--radius-md); font-family: monospace; font-size: 1.1rem; color: var(--accent-cyan); margin-bottom: 1.5rem; display:inline-block;">
        {html.escape(c.get('formula_latex', ''))}
      </div>

      <h3 style="font-size: 1.25rem; font-weight: 700; margin-bottom: 1rem;">Frequently Asked Questions</h3>
      {"".join(faq_html_list)}
    </section>
  </main>

  <footer>
    <div class="container">
      <div class="footer-links">
        <a href="../index.html">Home</a>
        <a href="../sitemap.xml">Sitemap</a>
        <a href="{coffee_url}" target="_blank" rel="noopener">Support</a>
      </div>
      <p>&copy; {datetime.now().year} VoltCraft. Zero-cost, high-precision engineering tools.</p>
    </div>
  </footer>

  <script src="../app.js"></script>
  <script>
    // Custom calculation logic for this specific page
    function solve_{calc_id.replace('-', '_')}() {{
      {chr(10).join(['      ' + l for l in calc_js_lines])}
      
      // Compute specific formulas
      if ("{calc_id}" === "ohms-law-calculator") {{
        const r = voltage / (current || 1e-9);
        const p = voltage * current;
        document.getElementById('out_resistance').textContent = window.formatUnit(r, 'Ω');
        document.getElementById('out_power').textContent = window.formatUnit(p, 'W');
      }} else if ("{calc_id}" === "led-resistor-calculator") {{
        const vr = Math.max(0, v_supply - v_forward);
        const i_a = i_led / 1000.0;
        const r = vr / (i_a || 1e-9);
        const p = vr * i_a;
        document.getElementById('out_r_resistor').textContent = window.formatUnit(r, 'Ω');
        document.getElementById('out_p_resistor').textContent = window.formatUnit(p, 'W');
      }} else if ("{calc_id}" === "voltage-divider-calculator") {{
        const vout = vin * (r2 / (r1 + r2 || 1));
        const ratio = r2 / (r1 + r2 || 1);
        document.getElementById('out_vout').textContent = vout.toFixed(3) + " V";
        document.getElementById('out_ratio').textContent = ratio.toFixed(4);
      }} else if ("{calc_id}" === "battery-life-calculator") {{
        const hours = (capacity * (derate / 100.0)) / (current || 1e-9);
        document.getElementById('out_runtime_hours').textContent = hours.toFixed(1) + " hours";
        document.getElementById('out_runtime_days').textContent = (hours / 24.0).toFixed(2) + " days";
      }} else if ("{calc_id}" === "pcb-trace-width-calculator") {{
        const area_ext = Math.pow(current / (0.048 * Math.pow(temp_rise, 0.44)), 1 / 0.725);
        const width_ext = area_ext / (cu_thickness * 1.378);
        document.getElementById('out_external_width').textContent = width_ext.toFixed(1) + " mils (" + (width_ext * 0.0254).toFixed(2) + " mm)";
        const area_int = Math.pow(current / (0.024 * Math.pow(temp_rise, 0.44)), 1 / 0.725);
        const width_int = area_int / (cu_thickness * 1.378);
        document.getElementById('out_internal_width').textContent = width_int.toFixed(1) + " mils (" + (width_int * 0.0254).toFixed(2) + " mm)";
      }} else if ("{calc_id}" === "555-timer-astable-calculator") {{
        const f = 1.44 / ((r1 + 2 * r2) * (c * 1e-6) || 1e-9);
        const duty = ((r1 + r2) / (r1 + 2 * r2 || 1)) * 100;
        document.getElementById('out_frequency').textContent = window.formatUnit(f, 'Hz');
        document.getElementById('out_duty_cycle').textContent = duty.toFixed(1) + " %";
      }} else if ("{calc_id}" === "rc-lowpass-filter-calculator") {{
        const fc = 1.0 / (2 * Math.PI * r * (c * 1e-9) || 1e-9);
        const tau = r * (c * 1e-9) * 1000;
        document.getElementById('out_fc').textContent = window.formatUnit(fc, 'Hz');
        document.getElementById('out_tau').textContent = tau.toFixed(2) + " ms";
      }} else if ("{calc_id}" === "dbm-to-watts-calculator") {{
        const mw = Math.pow(10, dbm / 10);
        const w = Math.pow(10, (dbm - 30) / 10);
        document.getElementById('out_watts').textContent = w >= 1 ? w.toFixed(2) + " W" : (w*1000).toFixed(2) + " mW";
        document.getElementById('out_milliwatts').textContent = mw.toFixed(2) + " mW";
      }} else if ("{calc_id}" === "wire-gauge-awg-calculator") {{
        const d_mm = 0.127 * Math.pow(92, (36 - awg) / 39);
        const r_per_m = 0.017241 / ((Math.PI * Math.pow(d_mm / 2, 2)));
        const vdrop = current * (r_per_m * length * 2);
        document.getElementById('out_diameter_mm').textContent = d_mm.toFixed(3) + " mm";
        document.getElementById('out_v_drop').textContent = vdrop.toFixed(3) + " V";
      }} else if ("{calc_id}" === "smd-resistor-code-calculator") {{
        let res = "Unknown code";
        const c_str = String(code).trim().toUpperCase();
        if (c_str.length === 3 && !isNaN(c_str)) {{
          const base = parseInt(c_str.substring(0, 2), 10);
          const mul = parseInt(c_str[2], 10);
          res = window.formatUnit(base * Math.pow(10, mul), 'Ω');
        }} else if (c_str.length === 4 && !isNaN(c_str)) {{
          const base = parseInt(c_str.substring(0, 3), 10);
          const mul = parseInt(c_str[3], 10);
          res = window.formatUnit(base * Math.pow(10, mul), 'Ω');
        }} else if (c_str.includes('R')) {{
          res = c_str.replace('R', '.') + " Ω";
        }}
        document.getElementById('out_resistance_str').textContent = res;
      }}
    }}

    // Bind slider & input 2-way syncing
    document.querySelectorAll('.num-input').forEach(inp => {{
      const slider = document.getElementById('slider_' + inp.id.replace('inp_', ''));
      if (slider) {{
        inp.addEventListener('input', () => {{ slider.value = inp.value; solve_{calc_id.replace('-', '_')}(); }});
        slider.addEventListener('input', () => {{ inp.value = slider.value; solve_{calc_id.replace('-', '_')}(); }});
      }} else {{
        inp.addEventListener('input', solve_{calc_id.replace('-', '_')});
      }}
    }});

    // Initial calculation
    solve_{calc_id.replace('-', '_')}();
  </script>
</body>
</html>"""

        with open(os.path.join(calc_dir, f"{calc_id}.html"), "w", encoding="utf-8") as f:
            f.write(page_html)

    print(f"Generated {len(calculators)} programmatic calculator pages in {calc_dir}")

def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    calcs_file = os.path.join(root_dir, "calculators.json")
    monetization_file = os.path.join(root_dir, "monetization.config.json")

    calculators = load_json(calcs_file)
    monetization = load_json(monetization_file)

    build_index_html(calculators, monetization, root_dir)
    build_programmatic_calculator_pages(calculators, monetization, root_dir)
    generate_sitemap(calculators, root_dir)
    generate_robots(root_dir)
    print("Static build and programmatic generation finished 100% successfully!")

if __name__ == "__main__":
    main()
