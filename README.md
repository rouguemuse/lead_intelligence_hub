# Context & Muse — High-Value Lead Intelligence & Prototype Studio

> High-leverage B2B sales intelligence, browser-driven reality checks, and conversion prototype studio for **Context & Muse Digital Systems Studio**.

---

## Overview

Context & Muse discovers established businesses ($5k–$20k+ budget capacity) experiencing expensive digital intake, lead routing, and conversion friction.

This engine enforces a strict **3-Tier Truth Model**:
$$\text{Observable Ground Truth (Evidence)} \longrightarrow \text{Interpreted Finding (Hypothesis Ledger)} \longrightarrow \text{Commercial Recommendation}$$

### The Core Workflow
1. **Scout:** Discovers established multi-location commercial operators and agency partners.
2. **Reality-Check Audit:** Investigates existing tech stacks (ServiceTitan, ScheduleEngine, HubSpot) to delete false positive assumptions before scoring.
3. **Approval:** Review vetted decision cards with verifiable evidence and screenshots.
4. **Proof:** Generates clean, standalone interactive conversion prototypes (`08_premium_mockup.html`).
5. **Outreach:** Generates copy-paste 3-sentence grounded emails and 60-second Loom video teardown scripts.

---

## Architecture & Strategic Boundaries

### The Standalone Conversion Layer Strategy
* **Preferred:** Modern/custom stack deployed on dedicated subdomains (e.g., `fleet.company.com`, `book.company.com`, or clean modal embeds).
* **Hard Disqualifier:** Zero direct WordPress theme editing, Elementor hacking, PHP maintenance, or legacy CMS maintenance.

---

## Quick Start

### 1. Run the Interactive Web Studio (Custom Filters & Prototypes)
```powershell
uv run python server.py
```
Open **[http://127.0.0.1:8420](http://127.0.0.1:8420)** to use the live dashboard with custom score sliders, lane filters, and 1-click outreach copy.

### 2. Run CLI Intelligence Dashboard
```powershell
# View vetted prospect cards
uv run python automator.py

# Display copy-paste outreach kit for a specific prospect
uv run python automator.py --kit occfixit
uv run python automator.py --kit theloomisagency
uv run python automator.py --kit kilgoreservice
uv run python automator.py --kit oldhamgoodwin

# Open interactive proof prototype in browser
uv run python automator.py --open occfixit
```

---

## Project Structure

```text
├── automator.py                    # Root Decision Dashboard & CLI
├── server.py                       # Interactive Studio Web Server (Port 8420)
├── studio_app.html                 # Interactive Web UI with custom filter controls
├── run_scout.bat                   # Windows batch quick launcher
├── pyproject.toml                  # Python package configuration
│
└── lead-intelligence/
    ├── leads.db                    # SQLite Database (evidence, findings, audits, assets)
    ├── reality_check_auditor.py    # Negative-check engine & Playwright browser auditor
    ├── mockup_engine.py            # Luxury interactive prototype & copy generator
    ├── scout_pipeline.py           # Ingestion & scoring pipeline
    ├── scout_learnings.md          # Self-improving learning loop & delivery boundaries
    │
    └── proof-assets/               # Generated Proof Suites & Mockups
        ├── occfixit/               # Optimum Collision (B2B Fleet Portal)
        ├── theloomisagency/        # The LOOMIS Agency (Franchise Systems Partner)
        ├── kilgoreservice/         # Kilgore Service (Commercial MEP Dispatch Portal)
        ├── oldhamgoodwin/          # Oldham Goodwin (Hotel Owner Intake Funnel)
        └── gopaschal/              # Paschal (Held on Watchlist)
```

---

## License
Proprietary & Confidential — Context & Muse Digital Systems Studio.
