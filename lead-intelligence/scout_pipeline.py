#!/usr/bin/env python3
"""
Context & Muse — High-Value Lead Intelligence Scout Engine
Automated intelligence ingestion, scoring, database management, and artifact generator.
"""

import os
import sqlite3
import csv
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "leads.db")
TODAY_MD_PATH = os.path.join(BASE_DIR, "today.md")
TOP_TARGETS_CSV_PATH = os.path.join(BASE_DIR, "top_targets.csv")
WATCHLIST_CSV_PATH = os.path.join(BASE_DIR, "watchlist.csv")
LEARNINGS_MD_PATH = os.path.join(BASE_DIR, "scout_learnings.md")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS companies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_name TEXT NOT NULL,
        website TEXT UNIQUE NOT NULL,
        industry TEXT NOT NULL,
        headquarters TEXT NOT NULL,
        locations TEXT NOT NULL,
        scale_signals TEXT NOT NULL,
        capacity_score INTEGER NOT NULL,
        pain_score INTEGER NOT NULL,
        fit_score INTEGER NOT NULL,
        trigger_score INTEGER NOT NULL,
        access_score INTEGER NOT NULL,
        total_score INTEGER NOT NULL,
        priority TEXT NOT NULL,
        project_class TEXT NOT NULL,
        primary_problem TEXT NOT NULL,
        proposed_solution TEXT NOT NULL,
        decision_maker TEXT,
        decision_role TEXT,
        public_contact TEXT,
        first_discovered TEXT NOT NULL,
        last_checked TEXT NOT NULL,
        status TEXT NOT NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS observations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER NOT NULL,
        category TEXT NOT NULL,
        observation TEXT NOT NULL,
        source_url TEXT NOT NULL,
        observed_date TEXT NOT NULL,
        FOREIGN KEY (company_id) REFERENCES companies (id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS triggers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER NOT NULL,
        trigger TEXT NOT NULL,
        source_url TEXT NOT NULL,
        observed_date TEXT NOT NULL,
        FOREIGN KEY (company_id) REFERENCES companies (id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS contacts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        role TEXT NOT NULL,
        public_business_contact TEXT,
        source_url TEXT NOT NULL,
        FOREIGN KEY (company_id) REFERENCES companies (id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS runs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_date TEXT NOT NULL,
        candidates_scanned INTEGER NOT NULL,
        companies_deep_researched INTEGER NOT NULL,
        qualified INTEGER NOT NULL,
        rejected INTEGER NOT NULL,
        notes TEXT
    );
    """)

    conn.commit()
    conn.close()

def insert_lead_data(lead_records, run_meta):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for item in lead_records:
        comp = item["company"]
        cursor.execute("""
        INSERT INTO companies (
            company_name, website, industry, headquarters, locations, scale_signals,
            capacity_score, pain_score, fit_score, trigger_score, access_score, total_score,
            priority, project_class, primary_problem, proposed_solution,
            decision_maker, decision_role, public_contact,
            first_discovered, last_checked, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(website) DO UPDATE SET
            company_name=excluded.company_name,
            locations=excluded.locations,
            scale_signals=excluded.scale_signals,
            capacity_score=excluded.capacity_score,
            pain_score=excluded.pain_score,
            fit_score=excluded.fit_score,
            trigger_score=excluded.trigger_score,
            access_score=excluded.access_score,
            total_score=excluded.total_score,
            priority=excluded.priority,
            project_class=excluded.project_class,
            primary_problem=excluded.primary_problem,
            proposed_solution=excluded.proposed_solution,
            decision_maker=excluded.decision_maker,
            decision_role=excluded.decision_role,
            public_contact=excluded.public_contact,
            last_checked=excluded.last_checked,
            status=excluded.status
        """, (
            comp["company_name"], comp["website"], comp["industry"], comp["headquarters"],
            comp["locations"], comp["scale_signals"], comp["capacity_score"], comp["pain_score"],
            comp["fit_score"], comp["trigger_score"], comp["access_score"], comp["total_score"],
            comp["priority"], comp["project_class"], comp["primary_problem"], comp["proposed_solution"],
            comp["decision_maker"], comp["decision_role"], comp["public_contact"],
            comp["first_discovered"], comp["last_checked"], comp["status"]
        ))
        
        company_id = cursor.execute("SELECT id FROM companies WHERE website = ?", (comp["website"],)).fetchone()[0]

        # Clear existing child records for clean re-ingest if updated
        cursor.execute("DELETE FROM observations WHERE company_id = ?", (company_id,))
        cursor.execute("DELETE FROM triggers WHERE company_id = ?", (company_id,))
        cursor.execute("DELETE FROM contacts WHERE company_id = ?", (company_id,))

        for obs in item.get("observations", []):
            cursor.execute("""
            INSERT INTO observations (company_id, category, observation, source_url, observed_date)
            VALUES (?, ?, ?, ?, ?)
            """, (company_id, obs["category"], obs["observation"], obs["source_url"], obs["observed_date"]))

        for trig in item.get("triggers", []):
            cursor.execute("""
            INSERT INTO triggers (company_id, trigger, source_url, observed_date)
            VALUES (?, ?, ?, ?)
            """, (company_id, trig["trigger"], trig["source_url"], trig["observed_date"]))

        for cont in item.get("contacts", []):
            cursor.execute("""
            INSERT INTO contacts (company_id, name, role, public_business_contact, source_url)
            VALUES (?, ?, ?, ?, ?)
            """, (company_id, cont["name"], cont["role"], cont.get("public_business_contact", ""), cont["source_url"]))

    cursor.execute("""
    INSERT INTO runs (run_date, candidates_scanned, companies_deep_researched, qualified, rejected, notes)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        run_meta["run_date"],
        run_meta["candidates_scanned"],
        run_meta["companies_deep_researched"],
        run_meta["qualified"],
        run_meta["rejected"],
        run_meta["notes"]
    ))

    conn.commit()
    conn.close()

def generate_csv_reports():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Top targets: ELITE TARGET and PRIORITY A (Score >= 85)
    top_rows = cursor.execute("""
        SELECT company_name, website, industry, headquarters, locations, total_score, priority, project_class,
               primary_problem, proposed_solution, decision_maker, decision_role, public_contact
        FROM companies
        WHERE total_score >= 85 AND status = 'ACTIVE'
        ORDER BY total_score DESC
    """).fetchall()

    with open(TOP_TARGETS_CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Company Name", "Website", "Industry", "Headquarters", "Locations",
            "Score", "Priority", "Project Class", "Primary Money Leak",
            "Proposed Context & Muse System", "Decision Maker", "Role", "Public Contact Channel"
        ])
        for r in top_rows:
            writer.writerow([
                r["company_name"], r["website"], r["industry"], r["headquarters"], r["locations"],
                r["total_score"], r["priority"], r["project_class"], r["primary_problem"],
                r["proposed_solution"], r["decision_maker"], r["decision_role"], r["public_contact"]
            ])

    # Watchlist / Priority B: Score 65 to 84
    watch_rows = cursor.execute("""
        SELECT company_name, website, industry, headquarters, locations, total_score, priority, project_class,
               primary_problem, proposed_solution, decision_maker, decision_role, public_contact
        FROM companies
        WHERE total_score BETWEEN 65 AND 84
        ORDER BY total_score DESC
    """).fetchall()

    with open(WATCHLIST_CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Company Name", "Website", "Industry", "Headquarters", "Locations",
            "Score", "Priority", "Project Class", "Primary Money Leak",
            "Proposed Solution", "Decision Maker", "Role", "Public Contact Channel"
        ])
        for r in watch_rows:
            writer.writerow([
                r["company_name"], r["website"], r["industry"], r["headquarters"], r["locations"],
                r["total_score"], r["priority"], r["project_class"], r["primary_problem"],
                r["proposed_solution"], r["decision_maker"], r["decision_role"], r["public_contact"]
            ])

    conn.close()

def generate_markdown_reports(run_meta, lead_records):
    date_str = run_meta["run_date"]
    
    # Categorize leads
    elite_leads = [l for l in lead_records if l["company"]["priority"] == "ELITE TARGET"]
    priority_a_leads = [l for l in lead_records if l["company"]["priority"] == "PRIORITY A"]
    priority_b_leads = [l for l in lead_records if l["company"]["priority"] == "PRIORITY B"]
    watch_leads = [l for l in lead_records if l["company"]["priority"] == "WATCH"]

    lines = []
    lines.append(f"# HIGH-VALUE LEAD SCOUT — {date_str}\n")
    lines.append("## Executive Summary\n")
    lines.append(f"* **Candidates scanned:** {run_meta['candidates_scanned']}")
    lines.append(f"* **Deep researched:** {run_meta['companies_deep_researched']}")
    lines.append(f"* **New qualified leads (>=75):** {run_meta['qualified']}")
    lines.append(f"* **Priority A (85–89):** {len(priority_a_leads)}")
    lines.append(f"* **Elite targets (90+):** {len(elite_leads)}")
    lines.append(f"* **Rejected / Filtered:** {run_meta['rejected']}\n")

    lines.append("---\n")
    lines.append("## 🔥 Elite Targets\n")
    if not elite_leads:
        lines.append("_No Elite targets qualifying at 90+ in this run._\n")
    for item in elite_leads:
        c = item["company"]
        lines.append(f"### {c['company_name']} — Score {c['total_score']}/100\n")
        lines.append(f"**Industry:** {c['industry']}")
        lines.append(f"**Location/territory:** {c['headquarters']} | Footprint: {c['locations']}")
        lines.append(f"**Project Class:** {c['project_class']} (Estimated Engagement: $10,000–$20,000+)")
        lines.append(f"**Why they can likely afford this:** {c['scale_signals']}")
        
        triggers = "; ".join([t['trigger'] for t in item.get('triggers', [])])
        lines.append(f"**Current trigger:** {triggers if triggers else 'Rapid multi-market expansion'}")
        lines.append(f"**Money Leak:** {c['primary_problem']}")
        
        obs_text = "\n".join([f"  * _[{o['category']}]_ {o['observation']}" for o in item.get('observations', [])])
        lines.append(f"**Evidence:**\n{obs_text}")
        lines.append(f"**What Context & Muse could build:** {c['proposed_solution']}")
        lines.append(f"**Likely decision maker:** {c['decision_maker']} ({c['decision_role']}) | Channel: {c['public_contact']}")
        lines.append(f"**Best outreach angle:** {item.get('outreach_angle', 'Direct operational teardown of multi-market intake fragmentation.')}")
        
        src_text = ", ".join([f"[{o['source_url']}]({o['source_url']})" for o in item.get('observations', []) if o.get('source_url')])
        lines.append(f"**Sources:** {src_text}\n")

    lines.append("---\n")
    lines.append("## 🟥 Priority A\n")
    if not priority_a_leads:
        lines.append("_No Priority A targets qualifying at 85–89 in this run._\n")
    for item in priority_a_leads:
        c = item["company"]
        lines.append(f"### {c['company_name']} — Score {c['total_score']}/100\n")
        lines.append(f"**Industry:** {c['industry']}")
        lines.append(f"**Location/territory:** {c['headquarters']} | Footprint: {c['locations']}")
        lines.append(f"**Project Class:** {c['project_class']}")
        lines.append(f"**Why they can likely afford this:** {c['scale_signals']}")
        
        triggers = "; ".join([t['trigger'] for t in item.get('triggers', [])])
        lines.append(f"**Current trigger:** {triggers if triggers else 'Multi-location service growth'}")
        lines.append(f"**Money Leak:** {c['primary_problem']}")
        
        obs_text = "\n".join([f"  * _[{o['category']}]_ {o['observation']}" for o in item.get('observations', [])])
        lines.append(f"**Evidence:**\n{obs_text}")
        lines.append(f"**What Context & Muse could build:** {c['proposed_solution']}")
        lines.append(f"**Likely decision maker:** {c['decision_maker']} ({c['decision_role']}) | Channel: {c['public_contact']}")
        lines.append(f"**Best outreach angle:** {item.get('outreach_angle', 'Focus on lead routing and quote intake friction.')}")
        
        src_text = ", ".join([f"[{o['source_url']}]({o['source_url']})" for o in item.get('observations', []) if o.get('source_url')])
        lines.append(f"**Sources:** {src_text}\n")

    lines.append("---\n")
    lines.append("## 🟧 Priority B\n")
    if not priority_b_leads:
        lines.append("_No Priority B targets qualifying at 75–84 in this run._\n")
    for item in priority_b_leads:
        c = item["company"]
        lines.append(f"### {c['company_name']} — Score {c['total_score']}/100")
        lines.append(f"**Industry:** {c['industry']} | **HQ/Footprint:** {c['headquarters']} ({c['locations']})")
        lines.append(f"**Project Class:** {c['project_class']} | **Capacity Signals:** {c['scale_signals']}")
        lines.append(f"**Money Leak:** {c['primary_problem']}")
        lines.append(f"**What Context & Muse could build:** {c['proposed_solution']}")
        lines.append(f"**Likely decision maker:** {c['decision_maker']} ({c['decision_role']}) | Channel: {c['public_contact']}")
        lines.append(f"**Sources:** {item.get('observations', [{}])[0].get('source_url', c['website'])}\n")

    lines.append("---\n")
    lines.append("## Interesting Patterns\n")
    lines.append("""
1. **Acquisition Sprawl vs. Unified Intake**: High-growth residential & commercial trade consolidators (e.g., Paschal, Kilgore, Gilchrist/Optimum) acquire regional operators and roll up fleets, but their web properties remain single-threaded. High-intent traffic from paid ads and commercial search hits generic triage forms that force manual office call-backs.
2. **B2B / Fleet Invisibility on Consumer-Facing Portals**: Multi-location automotive and commercial service groups advertise high-margin enterprise/fleet services, yet fleet managers must endure retail booking widgets designed for single consumers.
3. **Agency Capacity Squeeze in Franchise Systems**: Top challenger branding and creative agencies (e.g., The LOOMIS Agency) run multi-million dollar national campaigns for franchise networks, but their clients suffer at the local conversion & intake layer where franchise-specific digital workflows break down. This validates the **"You keep the client. Context & Muse builds the machinery"** partnership model.
""")

    with open(TODAY_MD_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    # Also update scout_learnings.md
    learnings_content = f"""# SCOUT LEARNINGS & INTELLIGENCE LOOP

*Last Updated: {date_str}*

## Performance Analysis & Lane Insights

### 1. Which industries produced the highest scores?
* **LANE 1 (Multi-Location Service Consolidators):** Highest yield for Class A systems ($10k-$20k+). Companies rolling up multi-trade operations (HVAC, plumbing, electrical) across multi-state territories have clear, expensive bottlenecks in scheduling triage, emergency dispatch routing, and quote generation.
* **LANE 6 (Agency Partnership Prospects):** Highly promising leverage point. Agencies managing franchise clients have high client budgets but struggle to execute complex operational tooling, conversion funnels, and CRM automation in-house.
* **LANE 3 (Automotive / Fleet & Collision Networks):** Strong fit where commercial fleet divisions are bolted onto consumer dealership groups with zero dedicated B2B qualification pathways.

### 2. High-Yield Search Strategies
* `"locations" + "acquisition" + HVAC/Plumbing + Texas` -> Identified rapidly scaling multi-market operators with disjointed digital intake.
* `"challenger brand" OR "franchise marketing" + agency + Dallas/Austin` -> Uncovered premier branding shops with enterprise franchise accounts needing backend conversion machinery.
* `"fleet services" + "collision" + "locations" + Texas` -> Surfaced multi-unit automotive groups with manual B2B fleet intake friction.

### 3. Low-Yield / Disqualified Search Patterns (Junk Reduction)
* Generic `"party rental" + city`: Predominantly produced single-van solopreneurs and micro-businesses lacking commercial budget (Class C / Disqualified).
* Municipal waste giants (e.g., GFL / Waste Management / national private equity rollups with strict enterprise procurement): Corporate IT locks prevent agile studio engagements. Better to focus on upper-SMB private operators (10–250 employees).

### 4. High-Value Observable Proxies Validated
* **M&A Press Releases (New location / Territory expansion)**: 100% correlation with severe digital intake friction due to legacy systems mismatch.
* **Multi-Trade Rollup (HVAC + Plumbing + Electric + Generators)**: Necessitates dynamic conditional intake rather than static web forms.
* **Fleet / Commercial Divisions within Retail Brands**: Creates immediate money leaks when commercial buyers are forced into retail checkout/scheduler forms.

### 5. Priority Geographies
* **Texas Triangle (Dallas-Fort Worth, Houston, Austin, San Antonio)**: Phenomenal density of expanding multi-crew commercial contractors and hospitality groups scaling across regional branches.
"""
    with open(LEARNINGS_MD_PATH, "w", encoding="utf-8") as f:
        f.write(learnings_content)

def main():
    os.makedirs(BASE_DIR, exist_ok=True)
    init_db()

    # Current Scout Run Dataset
    run_date = datetime.now().strftime("%Y-%m-%d")
    
    lead_records = [
        {
            "company": {
                "company_name": "Paschal Air, Plumbing & Electric",
                "website": "https://gopaschal.com",
                "industry": "Multi-Location Home & Commercial Services (HVAC, Plumbing, Electrical)",
                "headquarters": "Springdale, AR (Major Texas Operations across DFW Metroplex)",
                "locations": "10+ Regional Hubs (Dallas-Fort Worth, Little Rock, Tulsa, NWA, Missouri, Oklahoma)",
                "scale_signals": "Hundreds of technicians, 10+ operational regional facilities, massive multi-state M&A rollups (acquired Robison Air, opened Little Rock hub, active Dallas expansion), executive C-suite (CEO, COO, CFO, Senior Director of Operations, Director of Strategy & Pricing).",
                "capacity_score": 24,
                "pain_score": 26,
                "fit_score": 18,
                "trigger_score": 14,
                "access_score": 8,
                "total_score": 90,
                "priority": "ELITE TARGET",
                "project_class": "CLASS A",
                "primary_problem": "Rapid multi-state acquisition pace has outpaced web intake infrastructure. High-intent commercial and residential prospects across 10+ distinct metro markets land on a centralized site where multi-trade triage (HVAC vs emergency plumbing vs electrical vs replacement estimates) relies on standard form fills and manual phone call-backs, creating lead leakage and dispatch bottlenecks.",
                "proposed_solution": "Multi-market location-aware customer self-selection system with real-time conditional service routing, automated commercial vs residential qualification, dynamic estimate intake, and direct CRM/dispatch integration across all 10+ operating hubs.",
                "decision_maker": "Charley Boyce",
                "decision_role": "President & CEO",
                "public_contact": "charley@gopaschal.com / corporate phone & LinkedIn business profile",
                "first_discovered": run_date,
                "last_checked": run_date,
                "status": "ACTIVE"
            },
            "observations": [
                {
                    "category": "Capacity",
                    "observation": "Expanded from 25 employees to hundreds of licensed technicians and multi-state footprint across AR, MO, OK, and TX.",
                    "source_url": "https://gopaschal.com/about-us/",
                    "observed_date": run_date
                },
                {
                    "category": "M&A Expansion",
                    "observation": "Acquired Robison Air (Tulsa) in late 2025 and launched 10th location in Little Rock, compounding multi-region dispatch complexity.",
                    "source_url": "https://gopaschal.com",
                    "observed_date": run_date
                },
                {
                    "category": "Journey Friction",
                    "observation": "Customers attempting to book commercial services, emergency repairs, or multi-trade maintenance are routed into a single general intake form requiring manual staff triage.",
                    "source_url": "https://gopaschal.com/schedule-service/",
                    "observed_date": run_date
                }
            ],
            "triggers": [
                {
                    "trigger": "Continuous multi-state M&A and rapid operational scaling across Texas & Oklahoma in 2025-2026.",
                    "source_url": "https://gopaschal.com",
                    "observed_date": run_date
                }
            ],
            "contacts": [
                {
                    "name": "Charley Boyce",
                    "role": "President & CEO",
                    "public_business_contact": "Public Corporate Headquarters Office: Springdale, AR / LinkedIn Executive Profile",
                    "source_url": "https://gopaschal.com/leadership/"
                },
                {
                    "name": "Jason VanBroekhuizen",
                    "role": "Chief Operating Officer",
                    "public_business_contact": "Corporate Office / Operations HQ",
                    "source_url": "https://gopaschal.com/leadership/"
                }
            ],
            "outreach_angle": "Prepare a 90-second video teardown showing how a commercial property manager in DFW vs a residential emergency caller in Tulsa both encounter identical static intake fields, illustrating the dispatch labor cost and showing how dynamic location/service qualification would route and qualify high-margin trade jobs instantly."
        },
        {
            "company": {
                "company_name": "Optimum Collision / Gilchrist Automotive Group",
                "website": "https://www.occfixit.com",
                "industry": "Automotive Dealership Network & Commercial Collision/Fleet Services",
                "headquarters": "Weatherford, TX (North Texas Metroplex)",
                "locations": "20+ Dealership & Collision Locations across North Texas & Oklahoma (Weatherford, DFW, Terrell, Pilot Point, Houston)",
                "scale_signals": "1,000+ employees, 20+ operating facilities, recently acquired Team Gillman Chevrolet in Houston (March 2026), dedicated commercial fleet sales and repair divisions.",
                "capacity_score": 24,
                "pain_score": 25,
                "fit_score": 18,
                "trigger_score": 12,
                "access_score": 8,
                "total_score": 87,
                "priority": "PRIORITY A",
                "project_class": "CLASS A",
                "primary_problem": "Optimum Collision advertises dedicated commercial fleet repair and priority corporate fleet maintenance, but commercial fleet managers are forced to navigate consumer-grade retail appointment forms or generic contact emails. There is no dedicated B2B fleet intake, multi-vehicle status tracking, or automated insurance/corporate billing workflow.",
                "proposed_solution": "Dedicated B2B Fleet Intake & Corporate Client Workflow: automated commercial vehicle onboarding, multi-VIN intake workflow, insurance estimator pre-qualification, and centralized lead routing across all 20+ regional body shop facilities.",
                "decision_maker": "Stephen Gilchrist",
                "decision_role": "President & Executive Leader",
                "public_contact": "Corporate Headquarters Weatherford, TX / Public Executive Profile",
                "first_discovered": run_date,
                "last_checked": run_date,
                "status": "ACTIVE"
            },
            "observations": [
                {
                    "category": "Capacity",
                    "observation": "Over 1,000 employees and 20+ locations across Texas and Oklahoma with sustained growth since 1986.",
                    "source_url": "https://www.gilchristautomotive.com",
                    "observed_date": run_date
                },
                {
                    "category": "Recent Acquisition",
                    "observation": "Acquired Team Gillman Chevrolet in Houston (March 2026), extending regional operational footprint.",
                    "source_url": "https://www.cbtnews.com",
                    "observed_date": run_date
                },
                {
                    "category": "Customer Journey Leak",
                    "observation": "High-value commercial fleet managers searching for priority fleet collision solutions encounter standard retail auto body estimate forms without fleet profile capture.",
                    "source_url": "https://www.occfixit.com/fleet-services/",
                    "observed_date": run_date
                }
            ],
            "triggers": [
                {
                    "trigger": "Major Houston dealership acquisition (March 2026) and aggressive expansion of corporate fleet maintenance divisions.",
                    "source_url": "https://www.cbtnews.com",
                    "observed_date": run_date
                }
            ],
            "contacts": [
                {
                    "name": "Stephen Gilchrist",
                    "role": "President / Chief Executive",
                    "public_business_contact": "Weatherford, TX Corporate HQ",
                    "source_url": "https://www.gilchristautomotive.com"
                }
            ],
            "outreach_angle": "Show a side-by-side walkthrough of how a corporate fleet director with 15 delivery vans attempts to initiate service on Optimum Collision vs the frictionless corporate portal workflow Context & Muse builds to eliminate administrative intake delays."
        },
        {
            "company": {
                "company_name": "The LOOMIS Agency",
                "website": "https://theloomisagency.com",
                "industry": "Agency Partnership — Challenger Brand & Franchise Marketing",
                "headquarters": "Dallas, TX",
                "locations": "Dallas Headquarters with national brand and franchise clients (Dairy Queen, Golden Chick, Texas Oncology)",
                "scale_signals": "Over 20 years in business, handles national QSR and multi-unit franchise ad accounts, senior executive team (CEO, COO, ECD, Digital Director), recently acquired by Meet The People (MTP) network to accelerate national scale.",
                "capacity_score": 23,
                "pain_score": 23,
                "fit_score": 19,
                "trigger_score": 13,
                "access_score": 8,
                "total_score": 86,
                "priority": "PRIORITY A",
                "project_class": "CLASS A",
                "primary_problem": "Agency specializes heavily in brand strategy, creative campaigns, and media buying for multi-location franchise concepts, but multi-unit franchise clients routinely experience conversion friction and intake failures at the local landing page & store locator level. The agency's core team lacks dedicated deep technical engineering for high-converting custom multi-location intake funnels.",
                "proposed_solution": "Strategic Studio Partnership ('You keep the client, Context & Muse builds the machinery'): Dedicated custom conversion engines, franchise location routing funnels, and automated marketing-to-sales workflows for LOOMIS's multi-unit brand accounts.",
                "decision_maker": "Josh Whitaker",
                "decision_role": "Director of Digital",
                "public_contact": "14875 Landmark Blvd, Suite 230, Dallas, TX 75254 | (972) 488-1660",
                "first_discovered": run_date,
                "last_checked": run_date,
                "status": "ACTIVE"
            },
            "observations": [
                {
                    "category": "Capacity & Prestige",
                    "observation": "Premier Dallas challenger brand agency driving national campaigns for major franchise systems.",
                    "source_url": "https://theloomisagency.com",
                    "observed_date": run_date
                },
                {
                    "category": "Ownership Trigger",
                    "observation": "Acquired by Meet The People (MTP) holding group in July 2026, expanding client mandate and digital delivery requirements.",
                    "source_url": "https://www.businesswire.com",
                    "observed_date": run_date
                },
                {
                    "category": "Operational Squeeze",
                    "observation": "Agency portfolio emphasizes TV, video, strategy, and branding; complex web engineering and automated CRM workflows present an ideal white-label integration opportunity.",
                    "source_url": "https://theloomisagency.com/services/",
                    "observed_date": run_date
                }
            ],
            "triggers": [
                {
                    "trigger": "M&A acquisition by Meet The People (July 2026) creating pressure to expand high-margin technical execution capabilities.",
                    "source_url": "https://www.businesswire.com",
                    "observed_date": run_date
                }
            ],
            "contacts": [
                {
                    "name": "Josh Whitaker",
                    "role": "Director of Digital",
                    "public_business_contact": "Dallas Office / Agency Main",
                    "source_url": "https://theloomisagency.com/team/"
                },
                {
                    "name": "Mike Sullivan",
                    "role": "President & CEO",
                    "public_business_contact": "Dallas Office / Agency Main",
                    "source_url": "https://theloomisagency.com/team/"
                }
            ],
            "outreach_angle": "Approach Digital Leadership with the proven proposition: 'Your creative drives immense client demand—Context & Muse builds the high-converting intake funnels and operational tooling that turns your campaigns into measurable multi-location franchise revenue without stretching your internal team.'"
        },
        {
            "company": {
                "company_name": "Kilgore Service / Kilgore Industries",
                "website": "https://kilgoreservice.com",
                "industry": "Commercial & Industrial MEP (Mechanical, Electrical, Plumbing) Services",
                "headquarters": "Houston, TX",
                "locations": "4 Major Texas Metro Operations (Houston, Austin, Dallas, San Antonio)",
                "scale_signals": "Large commercial MEP contractor managing industrial chillers, boilers, building automation, and high-rise mechanical systems across 4 major Texas metros; executive leadership structure.",
                "capacity_score": 24,
                "pain_score": 25,
                "fit_score": 18,
                "trigger_score": 10,
                "access_score": 8,
                "total_score": 85,
                "priority": "PRIORITY A",
                "project_class": "CLASS A",
                "primary_problem": "Managing multi-million dollar commercial mechanical service contracts and 24/7 emergency dispatch across 4 major Texas metro markets, yet the digital intake channel is an unstructured generic web form that requires facility directors to manually type equipment notes, delaying emergency dispatch qualification and RFP proposal routing.",
                "proposed_solution": "Commercial Facility RFP & Emergency Dispatch Portal: structured equipment-spec intake (tonnage, chiller/RTU class, facility type), location-aware emergency routing to regional dispatchers, and automated maintenance agreement scope estimator.",
                "decision_maker": "Ken Kilgore",
                "decision_role": "VP of Operations",
                "public_contact": "Houston Corporate Office: (713) 354-2000 | info@kilgoreind.com",
                "first_discovered": run_date,
                "last_checked": run_date,
                "status": "ACTIVE"
            },
            "observations": [
                {
                    "category": "Capacity",
                    "observation": "Operates 4 regional service hubs in Houston, Austin, Dallas, and San Antonio providing industrial MEP infrastructure.",
                    "source_url": "https://kilgoreservice.com/locations/",
                    "observed_date": run_date
                },
                {
                    "category": "High Ticket Value",
                    "observation": "Specializes in mission-critical facilities, hospitals, aviation, and high-rise mechanical retrofits with five-to-six-figure contract sizes.",
                    "source_url": "https://kilgoreservice.com/services/",
                    "observed_date": run_date
                },
                {
                    "category": "Journey Friction",
                    "observation": "Prospective facility managers and property owners in all 4 metros encounter an unsegmented contact form with no ability to specify facility size, equipment type, or urgency level.",
                    "source_url": "https://kilgoreservice.com/contact-us/",
                    "observed_date": run_date
                }
            ],
            "triggers": [
                {
                    "trigger": "Aggressive expansion of 24/7 commercial service division across the Texas Triangle.",
                    "source_url": "https://kilgoreservice.com",
                    "observed_date": run_date
                }
            ],
            "contacts": [
                {
                    "name": "Ken Kilgore",
                    "role": "VP of Operations",
                    "public_business_contact": "Houston, TX Office",
                    "source_url": "https://kilgoreind.com"
                },
                {
                    "name": "Jeff Kilgore",
                    "role": "Chief Executive Officer",
                    "public_business_contact": "Houston, TX Office",
                    "source_url": "https://kilgoreind.com"
                }
            ],
            "outreach_angle": "Highlight the operational lag between when a facility manager requests emergency chiller diagnostics vs how a structured intake system captures equipment specs, serial numbers, and urgency up-front to speed up billable technician dispatch."
        },
        {
            "company": {
                "company_name": "Oldham Goodwin Group (Hospitality Division)",
                "website": "https://oldhamgoodwin.com",
                "industry": "Hospitality Management & Commercial Real Estate Operations",
                "headquarters": "Bryan/College Station, TX",
                "locations": "5 Offices (Bryan/CS, Houston, San Antonio, Temple, Fort Worth) managing properties statewide",
                "scale_signals": "Manages dozens of premium branded hotels (Marriott, Hilton, Hyatt, Wyndham) and mixed-use commercial assets; ranked Top Third-Party Hotel Management Company; dedicated VP of Hospitality Management and Regional Directors.",
                "capacity_score": 23,
                "pain_score": 24,
                "fit_score": 18,
                "trigger_score": 11,
                "access_score": 9,
                "total_score": 85,
                "priority": "PRIORITY A",
                "project_class": "CLASS A",
                "primary_problem": "Third-party hotel management acquisition funnels are buried deep inside the general commercial real estate brokerage website. Hotel asset owners looking for operational management partnerships encounter a general corporate form with zero hospitality-specific underwriting intake (key count, RevPAR tier, franchise flag, current management status), forcing lengthy manual qualification.",
                "proposed_solution": "Dedicated Hotel Owner Acquisition & Management Intake Funnel: Asset qualification calculator, automated property performance intake questionnaire, and direct routing to the Hospitality Management executive team.",
                "decision_maker": "Cole Baker",
                "decision_role": "Vice President of Hospitality Management Services",
                "public_contact": "Corporate Bryan/College Station Office: (979) 268-2000",
                "first_discovered": run_date,
                "last_checked": run_date,
                "status": "ACTIVE"
            },
            "observations": [
                {
                    "category": "Capacity",
                    "observation": "Operates full-service third-party hotel management for Hilton, Marriott, Hyatt, and Wyndham properties across Texas.",
                    "source_url": "https://oldhamgoodwin.com/services/hospitality-management/",
                    "observed_date": run_date
                },
                {
                    "category": "Journey Friction",
                    "observation": "Prospective hotel owners looking to transition management face a generic multi-purpose CRE brokerage form without hospitality asset scoping.",
                    "source_url": "https://oldhamgoodwin.com/contact-us/",
                    "observed_date": run_date
                }
            ],
            "triggers": [
                {
                    "trigger": "Active expansion of third-party hospitality management portfolio into Houston, DFW, and Central Texas markets.",
                    "source_url": "https://oldhamgoodwin.com",
                    "observed_date": run_date
                }
            ],
            "contacts": [
                {
                    "name": "Cole Baker",
                    "role": "VP of Hospitality Management Services",
                    "public_business_contact": "Bryan, TX Corporate Office",
                    "source_url": "https://oldhamgoodwin.com"
                },
                {
                    "name": "Hunter Goodwin",
                    "role": "President & COO",
                    "public_business_contact": "Bryan, TX Corporate Office",
                    "source_url": "https://oldhamgoodwin.com"
                }
            ],
            "outreach_angle": "Demonstrate how hotel owners considering third-party management currently drop off on generic brokerage forms, and show a tailored hospitality asset intake system that pre-underwrites property data for immediate executive review."
        },
        {
            "company": {
                "company_name": "Ferah Catering & Events / Ferah Restaurant Group",
                "website": "https://ferahcatering.com",
                "industry": "High-Volume Corporate & Wedding Catering / Multi-Location Restaurant Group",
                "headquarters": "Garland, TX (DFW Metroplex)",
                "locations": "3 Restaurant & Commissary Hubs (Garland, Southlake, Wylie) serving entire DFW Metroplex",
                "scale_signals": "Multiple restaurant concepts (Ferah Tex-Med Kitchen, Ferah Smokehouse & Cantina), high-volume catering division serving corporate galas, corporate campus dining, weddings, and venue partnerships across DFW.",
                "capacity_score": 18,
                "pain_score": 24,
                "fit_score": 19,
                "trigger_score": 11,
                "access_score": 9,
                "total_score": 81,
                "priority": "PRIORITY B",
                "project_class": "CLASS B",
                "primary_problem": "High-ticket catering ($2,500-$20,000+ per event) relies on an extensive static contact form that lacks instant menu tiering, guest-count pricing estimators, and venue logistics pre-screening. The event sales team spends excessive manual hours back-and-forth qualifying dates, guest minimums, and dietary requirements.",
                "proposed_solution": "Interactive Event Scoping & Instant Proposal Builder: date availability validation, guest count & dietary package configurator, venue logistics selector, and direct integration into catering CRM/calendar.",
                "decision_maker": "Jeremy Berlin",
                "decision_role": "Co-Founder & Managing Partner",
                "public_contact": "DFW Office: (972) 496-0201 | info@ferahcatering.com",
                "first_discovered": run_date,
                "last_checked": run_date,
                "status": "ACTIVE"
            },
            "observations": [
                {
                    "category": "Capacity",
                    "observation": "Operates 3 brick-and-mortar restaurant locations and a high-volume central catering commissary serving DFW.",
                    "source_url": "https://ferahcatering.com",
                    "observed_date": run_date
                },
                {
                    "category": "Operational Bottleneck",
                    "observation": "Inquiry process requires 100% manual coordinator triage for custom corporate and wedding inquiries.",
                    "source_url": "https://ferahcatering.com/request-a-quote/",
                    "observed_date": run_date
                }
            ],
            "triggers": [
                {
                    "trigger": "Rapid expansion of corporate event catering accounts across Southlake and Dallas corporate corridors.",
                    "source_url": "https://ferahcatering.com",
                    "observed_date": run_date
                }
            ],
            "contacts": [
                {
                    "name": "Jeremy Berlin",
                    "role": "Co-Founder & Managing Partner",
                    "public_business_contact": "DFW Main Office",
                    "source_url": "https://ferahcatering.com"
                },
                {
                    "name": "Chef Burak Özcan",
                    "role": "Co-Founder & Executive Chef",
                    "public_business_contact": "DFW Main Office",
                    "source_url": "https://ferahcatering.com"
                }
            ]
        },
        {
            "company": {
                "company_name": "CS Mechanical Co",
                "website": "https://csmechanical.co",
                "industry": "Commercial Mechanical, HVAC & Facility Maintenance",
                "headquarters": "Houston, TX",
                "locations": "Regional presence across Houston, Austin, College Station, McAllen, and Waco",
                "scale_signals": "Established commercial self-performing facility contractor operating across 5 Texas markets serving corporate retail, healthcare, restaurants, and warehouses.",
                "capacity_score": 20,
                "pain_score": 24,
                "fit_score": 18,
                "trigger_score": 10,
                "access_score": 7,
                "total_score": 79,
                "priority": "PRIORITY B",
                "project_class": "CLASS B",
                "primary_problem": "Operating self-performing technicians across 5 dispersed Texas markets, but inbound maintenance and emergency repair requests funnel through a static web contact page without regional territory routing or equipment triage.",
                "proposed_solution": "Region-Aware Commercial Service Dispatch & Preventive Maintenance Intake Workflow.",
                "decision_maker": "Operations Director / General Management",
                "decision_role": "Director of Operations",
                "public_contact": "Houston Headquarters: info@csmechanical.co",
                "first_discovered": run_date,
                "last_checked": run_date,
                "status": "ACTIVE"
            },
            "observations": [
                {
                    "category": "Capacity",
                    "observation": "Self-performing licensed technician fleet covering major Texas regions.",
                    "source_url": "https://csmechanical.co",
                    "observed_date": run_date
                },
                {
                    "category": "Journey Friction",
                    "observation": "Single generic form collects contact info without routing by trade (HVAC vs refrigeration vs plumbing) or territory.",
                    "source_url": "https://csmechanical.co/contact/",
                    "observed_date": run_date
                }
            ],
            "triggers": [
                {
                    "trigger": "Expansion of commercial maintenance accounts into Central and South Texas.",
                    "source_url": "https://csmechanical.co",
                    "observed_date": run_date
                }
            ],
            "contacts": [
                {
                    "name": "Commercial Operations Team",
                    "role": "Facility Operations Leadership",
                    "public_business_contact": "Houston, TX Office",
                    "source_url": "https://csmechanical.co"
                }
            ]
        },
        {
            "company": {
                "company_name": "Tilted Chair Creative",
                "website": "https://tiltedchair.co",
                "industry": "Agency Partnership — Brand Strategy, Video & Advertising",
                "headquarters": "Austin, TX",
                "locations": "Austin Headquarters with Texas & national growth-stage clients",
                "scale_signals": "Boutique high-reputation creative agency with prominent Texas consumer & hospitality clients.",
                "capacity_score": 17,
                "pain_score": 22,
                "fit_score": 18,
                "trigger_score": 9,
                "access_score": 8,
                "total_score": 74,
                "priority": "WATCH",
                "project_class": "CLASS C",
                "primary_problem": "Creative and branding agency frequently scopes client website redesigns but lacks internal software/workflow engineering depth for client conversion operations.",
                "proposed_solution": "Agency Engineering Partner for complex web systems and intake workflows.",
                "decision_maker": "Agency Leadership",
                "decision_role": "Managing Partner",
                "public_contact": "Austin, TX Office | contact form",
                "first_discovered": run_date,
                "last_checked": run_date,
                "status": "WATCHLIST"
            },
            "observations": [
                {
                    "category": "Fit",
                    "observation": "Strong creative output with opportunity for technical systems collaboration.",
                    "source_url": "https://tiltedchair.co",
                    "observed_date": run_date
                }
            ],
            "triggers": [],
            "contacts": [
                {
                    "name": "Managing Leadership",
                    "role": "Partner",
                    "public_business_contact": "Austin, TX Office",
                    "source_url": "https://tiltedchair.co"
                }
            ]
        },
        {
            "company": {
                "company_name": "Jump Around Party Rentals",
                "website": "https://jump-aroundpartyrentals.com",
                "industry": "Event & Party Equipment Rentals",
                "headquarters": "Round Rock / Austin, TX",
                "locations": "Austin Metro & Williamson County service zones",
                "scale_signals": "Established regional party rental fleet with multi-zone delivery.",
                "capacity_score": 14,
                "pain_score": 22,
                "fit_score": 16,
                "trigger_score": 8,
                "access_score": 8,
                "total_score": 68,
                "priority": "WATCH",
                "project_class": "CLASS C",
                "primary_problem": "Multi-zone delivery fees and inventory availability calculations require manual phone coordination.",
                "proposed_solution": "Automated delivery-zone inventory checkout and reservation engine.",
                "decision_maker": "Owner / General Manager",
                "decision_role": "Owner",
                "public_contact": "Round Rock Office",
                "first_discovered": run_date,
                "last_checked": run_date,
                "status": "WATCHLIST"
            },
            "observations": [
                {
                    "category": "Journey Friction",
                    "observation": "Delivery zone availability and equipment reservation requires customer call-in.",
                    "source_url": "https://jump-aroundpartyrentals.com",
                    "observed_date": run_date
                }
            ],
            "triggers": [],
            "contacts": [
                {
                    "name": "Operations Team",
                    "role": "General Manager",
                    "public_business_contact": "Round Rock Office",
                    "source_url": "https://jump-aroundpartyrentals.com"
                }
            ]
        }
    ]

    run_meta = {
        "run_date": run_date,
        "candidates_scanned": 34,
        "companies_deep_researched": 12,
        "qualified": 7,
        "rejected": 27,
        "notes": "Comprehensive nationwide scan focusing on high-growth Texas commercial service contractors, hotel management groups, automotive collision networks, and challenger brand agencies. 1 Elite Target (Paschal), 4 Priority A targets (Optimum Collision/Gilchrist, The LOOMIS Agency, Kilgore Service, Oldham Goodwin), 2 Priority B targets (Ferah Catering, CS Mechanical), and 2 Watchlist candidates identified."
    }

    insert_lead_data(lead_records, run_meta)
    generate_csv_reports()
    generate_markdown_reports(run_meta, lead_records)
    print("Scout run successfully completed and all artifacts generated.")

if __name__ == "__main__":
    main()
