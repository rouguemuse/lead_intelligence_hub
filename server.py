#!/usr/bin/env python3
"""
Context & Muse — Interactive Lead Intelligence & Prototype Studio Server
Serves a unified interactive web application with custom filtering, dynamic parameter controls,
live outreach kit generators, and standalone prototype viewers.
"""

import os
import sys
import json
import sqlite3
import urllib.parse
from http.server import HTTPServer, SimpleHTTPRequestHandler
import webbrowser
import threading

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LEAD_INTEL_DIR = os.path.join(BASE_DIR, "lead-intelligence")
DB_PATH = os.path.join(LEAD_INTEL_DIR, "leads.db")
PORT = 8420

class IntelligenceStudioHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        
        # API: Fetch all companies with verified evidence and observations
        if path == "/api/leads":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            
            data = self._get_leads_data()
            self.wfile.write(json.dumps(data).encode("utf-8"))
            return

        # Serve static assets from proof-assets
        if path.startswith("/proof-assets/"):
            file_subpath = path.replace("/proof-assets/", "")
            target_path = os.path.join(LEAD_INTEL_DIR, "proof-assets", file_subpath)
            if os.path.exists(target_path) and os.path.isfile(target_path):
                self.send_response(200)
                if target_path.endswith(".png"):
                    self.send_header("Content-Type", "image/png")
                elif target_path.endswith(".html"):
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                elif target_path.endswith(".md"):
                    self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.end_headers()
                with open(target_path, "rb") as f:
                    self.wfile.write(f.read())
                return

        # Default: Serve Main Interactive Dashboard
        if path == "/" or path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            with open(os.path.join(BASE_DIR, "studio_app.html"), "rb") as f:
                self.wfile.write(f.read())
            return

        super().do_GET()

    def _get_leads_data(self):
        leads = [
            {
                "id": "occfixit",
                "company_name": "Optimum Collision / Gilchrist Automotive",
                "website": "https://www.occfixit.com",
                "industry": "Automotive & Commercial Fleet Repair",
                "lane": "LANE 3 — Automotive & Fleet",
                "headquarters": "Weatherford, TX",
                "territory": "Texas",
                "locations_count": 20,
                "locations": "20+ Dealership & Collision Centers (Weatherford, DFW, Terrell, Pilot Point, Houston)",
                "total_score": 88,
                "priority": "PRIORITY A",
                "status": "VERIFIED_READY",
                "project_class": "CLASS A ($10k-$20k)",
                "decision_maker": "Stephen Gilchrist",
                "decision_role": "President",
                "scale_signals": "1,000+ employees, 20+ locations, acquired Team Gillman Chevrolet, dedicated fleet sales division.",
                "verified_gap": "B2B commercial fleet repair is advertised, but corporate fleet managers are forced into consumer retail body shop estimate forms with no multi-VIN intake or fleet portal.",
                "facts": [
                    "Corporate fleet managers looking for priority fleet repair are forced into consumer retail body shop estimate forms.",
                    "No multi-vehicle status tracking, corporate billing intake, or commercial fleet onboarding path.",
                    "High-margin commercial accounts face identical friction to single-car retail fender benders."
                ],
                "opportunity": "Standalone B2B Commercial Fleet Intake & Status Portal (fleet.occfixit.com).",
                "proof_path": "/proof-assets/occfixit/08_premium_mockup.html",
                "screenshot": "/proof-assets/occfixit/screenshots/01_hero_desktop.png",
                "has_wordpress": False,
                "delivery_model": "Standalone Subdomain (fleet.occfixit.com)"
            },
            {
                "id": "theloomisagency",
                "company_name": "The LOOMIS Agency",
                "website": "https://theloomisagency.com",
                "industry": "Agency Partnership — Multi-Unit Franchise Marketing",
                "lane": "LANE 6 — Agency Partnerships",
                "headquarters": "Dallas, TX",
                "territory": "Texas / National",
                "locations_count": 1,
                "locations": "Dallas Headquarters (National Franchise Accounts: Dairy Queen, Golden Chick)",
                "total_score": 86,
                "priority": "PRIORITY A",
                "status": "VERIFIED_READY",
                "project_class": "CLASS A ($10k-$20k)",
                "decision_maker": "Josh Whitaker / Mike Sullivan",
                "decision_role": "Director of Digital / CEO",
                "scale_signals": "20+ year challenger brand agency driving national campaigns for multi-unit franchise systems.",
                "verified_gap": "Agency sells high-tier brand strategy and media, but franchise clients lack dedicated technical conversion funnels and store locator intake machinery.",
                "facts": [
                    "Agency focuses on creative, media, and branding; complex web engineering and intake workflows are a delivery bottleneck.",
                    "Franchise clients experience local conversion drop-off on generic store/location landing pages."
                ],
                "opportunity": "Strategic Technical Partner ('You keep the client, Context & Muse builds the machinery').",
                "proof_path": "/proof-assets/theloomisagency/08_premium_mockup.html",
                "screenshot": "/proof-assets/theloomisagency/screenshots/01_hero_desktop.png",
                "has_wordpress": False,
                "delivery_model": "White-Label Modular Conversion Machinery"
            },
            {
                "id": "kilgoreservice",
                "company_name": "Kilgore Service / Kilgore Industries",
                "website": "https://kilgoreservice.com",
                "industry": "Commercial & Industrial MEP Services",
                "lane": "LANE 1 — Multi-Location Trade Services",
                "headquarters": "Houston, TX",
                "territory": "Texas",
                "locations_count": 4,
                "locations": "4 Major Texas Metro Operations (Houston, Austin, Dallas, San Antonio)",
                "total_score": 85,
                "priority": "PRIORITY A",
                "status": "VERIFIED_READY",
                "project_class": "CLASS A ($10k-$20k)",
                "decision_maker": "Ken Kilgore",
                "decision_role": "VP of Operations",
                "scale_signals": "Large commercial MEP contractor managing industrial chillers, boilers, and high-rise mechanical systems across 4 Texas metros.",
                "verified_gap": "5-to-6-figure industrial & commercial MEP inquiries across 4 Texas metros enter through an unsegmented static text form with zero equipment qualification.",
                "facts": [
                    "Facility directors cannot specify equipment tonnage, facility type (hospital, aviation, high-rise), or urgency level.",
                    "No dynamic routing between Houston, Austin, Dallas, and San Antonio dispatchers."
                ],
                "opportunity": "Standalone Commercial Facility RFP & Equipment Intake Portal (dispatch.kilgoreservice.com).",
                "proof_path": "/proof-assets/kilgoreservice/08_premium_mockup.html",
                "screenshot": "/proof-assets/kilgoreservice/screenshots/01_hero_desktop.png",
                "has_wordpress": False,
                "delivery_model": "Standalone Subdomain (dispatch.kilgoreservice.com)"
            },
            {
                "id": "oldhamgoodwin",
                "company_name": "Oldham Goodwin Group (Hospitality)",
                "website": "https://oldhamgoodwin.com",
                "industry": "Hospitality & Commercial Real Estate Management",
                "lane": "LANE 2 — Hospitality & Property Operations",
                "headquarters": "Bryan/College Station, TX",
                "territory": "Texas",
                "locations_count": 5,
                "locations": "5 Offices (Bryan/CS, Houston, San Antonio, Temple, Fort Worth) managing properties statewide",
                "total_score": 85,
                "priority": "PRIORITY A",
                "status": "VERIFIED_READY",
                "project_class": "CLASS A ($10k-$20k)",
                "decision_maker": "Cole Baker",
                "decision_role": "VP of Hospitality Management Services",
                "scale_signals": "Manages dozens of premium branded hotels (Marriott, Hilton, Hyatt, Wyndham) and mixed-use commercial assets.",
                "verified_gap": "Third-party hotel management acquisition paths are buried inside a general commercial real estate brokerage site without property underwriting intake.",
                "facts": [
                    "Hotel asset owners face a general form with zero hospitality-specific underwriting intake (keys, brand flags, location, operating metrics).",
                    "High-value management contract leads are forced into manual email qualification."
                ],
                "opportunity": "Dedicated Hotel Owner Acquisition & Management Intake Funnel (owners.oldhamgoodwin.com).",
                "proof_path": "/proof-assets/oldhamgoodwin/08_premium_mockup.html",
                "screenshot": "/proof-assets/oldhamgoodwin/screenshots/01_hero_desktop.png",
                "has_wordpress": True,
                "delivery_model": "Standalone Subdomain (Zero WordPress Theme Changes)"
            },
            {
                "id": "paschal",
                "company_name": "Paschal Air, Plumbing & Electric",
                "website": "https://gopaschal.com",
                "industry": "Multi-Trade Residential & Commercial Services",
                "lane": "LANE 1 — Multi-Location Trade Services",
                "headquarters": "Springdale, AR (DFW Operations)",
                "territory": "AR / TX / OK / MO",
                "locations_count": 10,
                "locations": "10+ Regional Hubs (Dallas-Fort Worth, Little Rock, Tulsa, NWA, Missouri, Oklahoma)",
                "total_score": 71,
                "priority": "WATCHLIST",
                "status": "WATCHLIST_HOLD",
                "project_class": "CLASS A ($10k-$20k)",
                "decision_maker": "Charley Boyce",
                "decision_role": "President & CEO",
                "scale_signals": "Hundreds of technicians, 10+ operational hubs, active multi-state M&A expansion.",
                "verified_gap": "REALITY CHECK APPLIED: High financial scale, but company already operates mature ScheduleEngine/ServiceTitan scheduling. Hold active outreach.",
                "facts": [
                    "High-value 'Free Second Opinion' offer is less prominent than standard service paths.",
                    "Homepage asks visitors to navigate service categories rather than starting with their specific problem."
                ],
                "opportunity": "Problem-first symptom selector (Held on Watchlist; do not pitch yet).",
                "proof_path": "/proof-assets/gopaschal/08_premium_mockup.html",
                "screenshot": "/proof-assets/gopaschal/screenshots/01_hero_desktop.png",
                "has_wordpress": True,
                "delivery_model": "Standalone Subdomain (book.gopaschal.com)"
            }
        ]
        return leads

def run_server():
    server = HTTPServer(("127.0.0.1", PORT), IntelligenceStudioHandler)
    print(f"[*] Context & Muse Intelligence Studio running at http://127.0.0.1:{PORT}")
    server.serve_forever()

if __name__ == "__main__":
    t = threading.Thread(target=run_server, daemon=True)
    t.start()
    webbrowser.open(f"http://127.0.0.1:{PORT}")
    print("Press Ctrl+C to stop.")
    try:
        while True:
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down server.")
