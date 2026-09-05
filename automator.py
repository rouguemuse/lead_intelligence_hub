#!/usr/bin/env python3
"""
Context & Muse — Client-Winning Intelligence Dashboard (Reality-Checked)
Prioritizes prospects with VERIFIED, observable gaps. Enforces negative checks to filter out false positives.
"""

import sys
import os
import argparse
import subprocess
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LEAD_INTEL_DIR = os.path.join(BASE_DIR, "lead-intelligence")
DB_PATH = os.path.join(LEAD_INTEL_DIR, "leads.db")
PROOF_DIR = os.path.join(LEAD_INTEL_DIR, "proof-assets")

# Ensure UTF-8 output on Windows terminal
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

PROSPECTS = {
    "occfixit": {
        "id": 2,
        "name": "Optimum Collision / Gilchrist Automotive",
        "score": 88,
        "domain": "https://www.occfixit.com",
        "decision_maker": "Stephen Gilchrist (President)",
        "why_pursue": "20+ dealership & collision locations in North Texas/OK, 1,000+ employees, dedicated commercial fleet sales division.",
        "verified_gap": "VERIFIED: Commercial fleet repair and priority fleet maintenance are advertised, but lack any dedicated B2B corporate intake or multi-VIN tracking portal.",
        "observations": [
            "Corporate fleet managers looking for priority fleet repair are forced into consumer retail body shop estimate forms.",
            "No multi-vehicle status tracking, corporate billing intake, or commercial fleet onboarding path.",
            "High-margin commercial accounts face identical friction to single-car retail fender benders."
        ],
        "opportunity": "Build a Standalone B2B Commercial Fleet Intake & Status Portal (fleet.occfixit.com).",
        "status": "PRIORITY A — READY FOR OUTREACH"
    },
    "theloomisagency": {
        "id": 3,
        "name": "The LOOMIS Agency",
        "score": 86,
        "domain": "https://theloomisagency.com",
        "decision_maker": "Josh Whitaker (Director of Digital) / Mike Sullivan (CEO)",
        "why_pursue": "Premier Dallas challenger brand agency managing multi-unit franchise clients (Dairy Queen, Golden Chick).",
        "verified_gap": "VERIFIED: Exceptional creative and advertising strategy, but multi-unit franchise clients lack custom conversion machinery.",
        "observations": [
            "Agency focuses on national creative, media, and branding; complex web engineering and intake workflows are a delivery bottleneck.",
            "Franchise clients experience local conversion drop-off on generic store/location landing pages."
        ],
        "opportunity": "Strategic Technical Partner ('You keep the client, Context & Muse builds the conversion machinery').",
        "status": "PRIORITY A — READY FOR OUTREACH"
    },
    "kilgoreservice": {
        "id": 4,
        "name": "Kilgore Service / Kilgore Industries",
        "score": 85,
        "domain": "https://kilgoreservice.com",
        "decision_maker": "Ken Kilgore (VP Operations)",
        "why_pursue": "4 major Texas metro operations (Houston, Austin, DFW, San Antonio), high-ticket commercial & industrial MEP.",
        "verified_gap": "VERIFIED: 4 Texas metro operations capture 5-figure commercial service requests through a completely unsegmented static contact form.",
        "observations": [
            "Facility directors cannot specify equipment tonnage, facility type (hospital, aviation, high-rise), or urgency level.",
            "No dynamic routing between Houston, Austin, Dallas, and San Antonio dispatchers."
        ],
        "opportunity": "Build a Standalone Commercial Facility RFP & Equipment Intake Portal (dispatch.kilgoreservice.com).",
        "status": "PRIORITY A — READY FOR OUTREACH"
    },
    "oldhamgoodwin": {
        "id": 5,
        "name": "Oldham Goodwin Group (Hospitality)",
        "score": 85,
        "domain": "https://oldhamgoodwin.com",
        "decision_maker": "Cole Baker (VP Hospitality Services)",
        "why_pursue": "Manages dozens of premium branded hotels (Marriott, Hilton, Hyatt, Wyndham) across Texas.",
        "verified_gap": "VERIFIED: Third-party hotel management inquiry paths are buried inside the general commercial real estate brokerage site.",
        "observations": [
            "Hotel asset owners face a general form with zero hospitality-specific underwriting intake (keys, brand flags, location, operating metrics).",
            "High-value management contract leads are forced into manual email qualification."
        ],
        "opportunity": "Dedicated Hotel Owner Acquisition & Management Intake Funnel.",
        "status": "PRIORITY A — READY FOR OUTREACH"
    },
    "paschal": {
        "id": 1,
        "name": "Paschal Air, Plumbing & Electric",
        "score": 71,
        "domain": "https://gopaschal.com",
        "decision_maker": "Charley Boyce (President & CEO)",
        "why_pursue": "Multi-state operator (AR, TX, OK, MO), 10+ regional hubs, hundreds of technicians.",
        "verified_gap": "REALITY CHECK APPLIED: Company quality is high, but obvious operational gap is not established. Do not assume broken dispatch or manufacturing claims.",
        "observations": [
            "High-value 'Free Second Opinion' offer is less prominent than standard service paths.",
            "Homepage asks visitors to navigate service categories rather than starting with their specific problem."
        ],
        "opportunity": "Problem-first symptom selector (Opportunity not yet validated for outreach).",
        "status": "WATCHLIST — DO NOT BUILD MOCKUP YET"
    }
}

def show_dashboard():
    print("\n" + "="*75)
    print("     CONTEXT & MUSE — PROSPECT INTELLIGENCE DASHBOARD (REALITY-CHECKED)")
    print("="*75)
    print(" [Standard: Only pursue prospects where a genuine, verified gap is proven.]\n")

    for key, p in PROSPECTS.items():
        is_watch = "WATCHLIST" in p['status']
        prefix = "⏸ [WATCHLIST]" if is_watch else "▶ [PRIORITY A]"
        
        print(f"{prefix} [{p['score']}/100] {p['name'].upper()}")
        print(f"  Status       : {p['status']}")
        print(f"  Target DM    : {p['decision_maker']}")
        print(f"  Why Pursue   : {p['why_pursue']}")
        print(f"  Reality Check: {p['verified_gap']}")
        print("  Key Facts    :")
        for obs in p['observations']:
            print(f"    • {obs}")
        print(f"  Opportunity  : {p['opportunity']}")
        
        if not is_watch:
            print(f"  Actions      :")
            print(f"    [1] View Brand Proof Concept : uv run python automator.py --open {key}")
            print(f"    [2] View Outreach Kit        : uv run python automator.py --kit {key}")
        else:
            print("  Action       : [HOLD] Further investigation required before outreach.")
        print("-" * 75)
    print()

def show_outreach_kit(key):
    if key not in PROSPECTS:
        print(f"[!] Prospect '{key}' not found. Available: {', '.join(PROSPECTS.keys())}")
        return

    p = PROSPECTS[key]
    first_name = p['decision_maker'].split()[0]
    domain_clean = p['domain'].replace('https://','').replace('www.','').rstrip('/')

    print("\n" + "="*75)
    print(f"  OUTREACH KIT — {p['name'].upper()}")
    print("="*75)

    print("\n--- 1. SHORT OUTREACH EMAIL (Grounded & Non-Presumptuous) ---")
    print(f"Subject: Quick idea for {p['name']}\n")
    print(f"Hi {first_name},\n")
    print(f"I was studying {p['name']}'s online customer journey recently.")
    print(f"I noticed that {p['observations'][0].lower()}")
    print(f"I also noticed {p['observations'][1].lower()}\n")
    print(f"I put together a quick interactive prototype showing how a standalone conversion layer (e.g. portal.{domain_clean}) could streamline that intake—without touching your existing website or CMS.\n")
    print(f"Here is a 60-second walkthrough: [Loom Link / Prototype Link]\n")
    print(f"Open to a quick look?")
    print(f"\nBest,\nContext & Muse Digital Systems Studio")

    print("\n--- 2. 60-TO-90 SECOND LOOM SCRIPT ---")
    print(f"[0:00 - 0:15] 'Hey {first_name}, quick note—I was looking at {p['name']}'s digital intake recently.'")
    print(f"[0:15 - 0:35] 'Your brand and reputation across {p['why_pursue'].split(',')[0]} are formidable. But right now, when someone tries to initiate service, {p['observations'][0].lower()}'")
    print(f"[0:35 - 0:55] *(Pull up concept on screen)* 'I built this quick prototype to show another approach. Instead of a generic contact form, the customer gets a dedicated, fast-track intake flow tailored to their exact need.'")
    print(f"[0:55 - 1:10] 'The best part is this lives as a clean standalone layer on something like portal.{domain_clean}—your current website stays completely untouched.'")
    print(f"[1:10 - 1:20] 'No sales pitch today—just wanted to share what we built. If you'd like the file or want to chat, let me know!'")

    print("\n--- 3. 1-PAGE SUMMARY ---")
    print(f"Company: {p['name']} ({p['domain']})")
    print(f"Key Executive: {p['decision_maker']}")
    print(f"Deployment Model: Standalone Subdomain (Zero CMS/WordPress changes)")
    print(f"Observed Facts:")
    for i, obs in enumerate(p['observations'], 1):
        print(f"  {i}. {obs}")
    print(f"Proposed System: {p['opportunity']}")
    print("="*75 + "\n")

def open_concept(key):
    target_file = os.path.join(PROOF_DIR, key, "08_premium_mockup.html")
    if os.path.exists(target_file):
        print(f"[*] Opening concept for {key} in browser...")
        subprocess.run(["powershell", "-c", f"Start-Process '{target_file}'"])
    else:
        print(f"[!] Concept file not found at: {target_file}")

def main():
    parser = argparse.ArgumentParser(description="Context & Muse — Client-Winning Intelligence Dashboard")
    parser.add_argument("--dashboard", action="store_true", help="View vetted high-value prospect decision dashboard")
    parser.add_argument("--kit", type=str, metavar="SLUG", help="Display the short outreach email & Loom script for a prospect")
    parser.add_argument("--open", type=str, metavar="SLUG", help="Open the interactive proof concept in your browser")

    args = parser.parse_args()

    if len(sys.argv) == 1 or args.dashboard:
        show_dashboard()
        return

    if args.kit:
        show_outreach_kit(args.kit.lower())
    elif args.open:
        open_concept(args.open.lower())

if __name__ == "__main__":
    main()
