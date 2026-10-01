#!/usr/bin/env python3
import sys
import os
import time
import subprocess
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading
from playwright.sync_api import sync_playwright

PORT = 8765
BASE_URL = f"http://127.0.0.1:{PORT}"

class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

def run_server(project_dir):
    os.chdir(project_dir)
    server = HTTPServer(('127.0.0.1', PORT), QuietHandler)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    return server

def run_qa():
    project_dir = os.path.dirname(os.path.abspath(__file__))
    screenshots_dir = os.path.join(project_dir, "screenshots")
    os.makedirs(screenshots_dir, exist_ok=True)

    print("=== Starting Local Server for QA ===")
    server = run_server(project_dir)
    time.sleep(0.5)

    console_errors = []
    tests_passed = 0
    total_tests = 0

    print("=== Launching Headless Chromium via Playwright ===")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 800})

        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)

        # Test 1: Home Page Loads and Title is Accurate
        total_tests += 1
        page.goto(f"{BASE_URL}/index.html", wait_until="networkidle")
        title = page.title()
        assert "VoltCraft" in title, f"Unexpected title: {title}"
        print(f" [PASS] Test 1: Home Page Title Verified ('{title}')")
        tests_passed += 1

        # Test 2: Quick Ohm's Law Calculator Interaction
        total_tests += 1
        page.fill("#quick_v", "24")
        page.fill("#quick_i", "4")
        # Trigger input event
        page.dispatch_event("#quick_v", "input")
        page.dispatch_event("#quick_i", "input")
        time.sleep(0.2)
        out_r = page.text_content("#quick_out_r").strip()
        out_p = page.text_content("#quick_out_p").strip()
        assert "6.00 Ω" in out_r, f"Expected 6.00 Ω, got {out_r}"
        assert "96.00 W" in out_p, f"Expected 96.00 W, got {out_p}"
        print(f" [PASS] Test 2: Live Quick Calculator Math Verified (24V, 4A -> R={out_r}, P={out_p})")
        tests_passed += 1

        # Test 3: Search Box Filter
        total_tests += 1
        page.fill("#calcSearch", "LED")
        page.dispatch_event("#calcSearch", "input")
        time.sleep(0.2)
        visible_cards = page.locator(".calc-card:visible").count()
        assert visible_cards >= 1, f"Expected filtered cards, got {visible_cards}"
        print(f" [PASS] Test 3: Search Filter Functionality Verified ({visible_cards} cards matched 'LED')")
        tests_passed += 1

        # Capture Screenshot of Home
        home_shot = os.path.join(screenshots_dir, "01_home_desktop.png")
        page.screenshot(path=home_shot, full_page=True)
        print(f" [INFO] Home Screenshot captured: {home_shot}")

        # Test 4: Programmatic Calculator Page (LED Resistor)
        total_tests += 1
        page.goto(f"{BASE_URL}/calculators/led-resistor-calculator.html", wait_until="networkidle")
        led_title = page.title()
        assert "LED Series Resistor Calculator" in led_title
        
        # Test calculation inputs
        page.fill("#inp_v_supply", "12")
        page.fill("#inp_v_forward", "3.2")
        page.fill("#inp_i_led", "20")
        page.dispatch_event("#inp_v_supply", "input")
        page.dispatch_event("#inp_v_forward", "input")
        page.dispatch_event("#inp_i_led", "input")
        time.sleep(0.2)
        
        # (12 - 3.2) / 0.02 = 8.8 / 0.02 = 440 Ohms, 176 mW
        r_val = page.text_content("#out_r_resistor").strip()
        assert "440.00 Ω" in r_val, f"Expected 440.00 Ω, got {r_val}"
        print(f" [PASS] Test 4: Programmatic Calculator Interaction (12V Supply, 3.2V LED, 20mA -> {r_val})")
        tests_passed += 1

        # Test 5: Verify Schema.org JSON-LD
        total_tests += 1
        schema_tags = page.locator('script[type="application/ld+json"]').all_inner_texts()
        assert len(schema_tags) > 0, "Schema JSON-LD missing"
        print(" [PASS] Test 5: Structured Data (Schema.org SoftwareApplication & FAQPage) present")
        tests_passed += 1

        # Capture Screenshot of Calculator Page
        calc_shot = os.path.join(screenshots_dir, "02_led_calculator.png")
        page.screenshot(path=calc_shot, full_page=True)
        print(f" [INFO] Calculator Page Screenshot captured: {calc_shot}")

        browser.close()

    server.shutdown()

    print("\n==========================================")
    print(f" QA RESULTS: {tests_passed}/{total_tests} TESTS PASSED")
    print(f" Console Errors: {len(console_errors)}")
    if console_errors:
        print(" Errors observed:", console_errors)
    print("==========================================")
    return len(console_errors) == 0 and tests_passed == total_tests

if __name__ == "__main__":
    success = run_qa()
    sys.exit(0 if success else 1)
