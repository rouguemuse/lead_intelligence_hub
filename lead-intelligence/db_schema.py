#!/usr/bin/env python3
"""
Context & Muse — Evidence-Backed Database Schema
Establishes the multi-layer evidence, observation, finding, and scoring schema.
"""

import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "leads.db")

def init_evidence_schema():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Core Companies Table
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

    # Audit Runs
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_runs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER,
        domain TEXT NOT NULL,
        started_at TEXT NOT NULL,
        completed_at TEXT,
        auditor_version TEXT NOT NULL,
        status TEXT NOT NULL,
        pages_crawled INTEGER DEFAULT 0,
        overall_confidence REAL DEFAULT 1.0,
        FOREIGN KEY (company_id) REFERENCES companies (id)
    );
    """)

    # Audit Observations (Ground Truth Layer)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_observations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        audit_id INTEGER NOT NULL,
        category TEXT NOT NULL,
        observation_type TEXT NOT NULL,
        page_url TEXT NOT NULL,
        element_selector TEXT,
        evidence_text TEXT NOT NULL,
        screenshot_path TEXT,
        raw_value TEXT,
        confidence REAL DEFAULT 1.0,
        severity TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY (audit_id) REFERENCES audit_runs (id)
    );
    """)

    # Audit Findings (Interpreted Layer & Hypothesis Ledger)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_findings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        audit_id INTEGER NOT NULL,
        vector TEXT NOT NULL,
        hypothesis_id TEXT NOT NULL,
        finding TEXT NOT NULL,
        evidence_summary TEXT NOT NULL,
        impact_hypothesis TEXT NOT NULL,
        confidence REAL DEFAULT 1.0,
        severity TEXT NOT NULL,
        recommendation TEXT NOT NULL,
        evidence_ids TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (audit_id) REFERENCES audit_runs (id)
    );
    """)

    # Funnel Scores (Defensible Metric Layer)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS funnel_scores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        audit_id INTEGER NOT NULL,
        vector TEXT NOT NULL,
        score REAL NOT NULL,
        confidence REAL DEFAULT 1.0,
        scoring_reason TEXT NOT NULL,
        FOREIGN KEY (audit_id) REFERENCES audit_runs (id)
    );
    """)

    # Proof Assets Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS proof_assets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER NOT NULL,
        audit_id INTEGER,
        asset_key TEXT NOT NULL,
        file_path TEXT NOT NULL,
        title TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY (company_id) REFERENCES companies (id),
        FOREIGN KEY (audit_id) REFERENCES audit_runs (id)
    );
    """)

    # Standard Run Tracker
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

if __name__ == "__main__":
    init_evidence_schema()
    print("Database evidence schema initialized.")
