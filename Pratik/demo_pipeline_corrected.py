"""
VANA MasterDB Foundation — Corrected Ingestion & Verification Pipeline
Group 2 Integration and Verification

Demonstrates:
  1. Relational schema creation with date_precision constraint added to observation.
  2. Loading and ingesting the corrected baseline JSON record (THANE_CREEK_MANGROVE_BASELINE_V0.1_CORRECTED.json).
  3. Proper foreign key validation (registers source, dataset, geography first).
  4. Retrieval join query proving the record, raw value, normalized value, run ID, and source details.
  5. Corrected, bug-free idempotency check (row count remains unchanged on duplicate insert).
  6. Rejection of invalid records.
"""

import sqlite3
import json
import os
from datetime import datetime, timezone

DB_PATH = "vana_demo_corrected.db"
JSON_PATH = "THANE_CREEK_MANGROVE_BASELINE_V0.1_CORRECTED.json"

if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

conn = sqlite3.connect(DB_PATH)
conn.execute("PRAGMA foreign_keys = ON")
cur = conn.cursor()

# 1. CREATE SCHEMA WITH CORRECTIONS
cur.executescript("""
CREATE TABLE schema_version (
    version TEXT PRIMARY KEY, applied_at TEXT NOT NULL, description TEXT NOT NULL
);
CREATE TABLE source (
    source_id TEXT PRIMARY KEY, source_type TEXT NOT NULL, title TEXT NOT NULL,
    publisher TEXT, url TEXT, citation TEXT, retrieved_at TEXT NOT NULL,
    is_synthetic INTEGER NOT NULL DEFAULT 0, notes TEXT
);
CREATE TABLE dataset (
    dataset_id TEXT PRIMARY KEY, dataset_name TEXT NOT NULL,
    source_id TEXT NOT NULL REFERENCES source(source_id),
    methodology TEXT, schema_version TEXT NOT NULL, created_at TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'REGISTERED'
);
CREATE TABLE geography (
    geo_id TEXT PRIMARY KEY, place_name TEXT NOT NULL,
    lat REAL NOT NULL, lon REAL NOT NULL, crs TEXT NOT NULL DEFAULT 'EPSG:4326', notes TEXT
);
CREATE TABLE observation (
    observation_id TEXT PRIMARY KEY, dataset_id TEXT NOT NULL REFERENCES dataset(dataset_id),
    geo_id TEXT REFERENCES geography(geo_id), observation_date TEXT, date_precision TEXT, species TEXT,
    observation_type TEXT NOT NULL, confidence TEXT, conflict_flag INTEGER NOT NULL DEFAULT 0,
    conflict_notes TEXT, created_at TEXT NOT NULL,
    CHECK (date_precision IN ('YYYY', 'YYYY-MM', 'YYYY-MM-DD'))
);
CREATE TABLE measurement (
    measurement_id TEXT PRIMARY KEY, observation_id TEXT NOT NULL REFERENCES observation(observation_id),
    metric_name TEXT NOT NULL, value REAL NOT NULL, unit TEXT NOT NULL, method TEXT,
    original_value_text TEXT, transform_applied TEXT, created_at TEXT NOT NULL
);
CREATE TABLE processing_run (
    run_id TEXT PRIMARY KEY, source_id TEXT NOT NULL REFERENCES source(source_id),
    dataset_id TEXT REFERENCES dataset(dataset_id), pipeline_stage TEXT NOT NULL,
    status TEXT NOT NULL, input_ref TEXT, output_ref TEXT, error_detail TEXT,
    started_at TEXT NOT NULL, finished_at TEXT, actor TEXT NOT NULL
);
CREATE TABLE provenance (
    provenance_id TEXT PRIMARY KEY, measurement_id TEXT NOT NULL REFERENCES measurement(measurement_id),
    source_id TEXT NOT NULL REFERENCES source(source_id), run_id TEXT REFERENCES processing_run(run_id),
    derivation_note TEXT NOT NULL, recorded_at TEXT NOT NULL
);
""")

cur.execute(
    "INSERT INTO schema_version VALUES (?,?,?)",
    ("0.1", datetime.now(timezone.utc).isoformat(),
     "Initial VANA foundation with date_precision support"),
)
conn.commit()
print("[1] Schema created with date_precision added to observation.")

# 2. INGEST CORRECTED JSON RECORD
with open(JSON_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)[0]

now_str = datetime.now(timezone.utc).isoformat()

# Register Source
src = data["source"]
cur.execute("""
    INSERT INTO source (source_id, source_type, title, publisher, url, citation, retrieved_at, is_synthetic, notes)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (src["source_id"], src["source_type"], src["title"], src["publisher"], src["url"], src["citation"], now_str, 0, src["notes"]))

# Register Dataset
ds = data["dataset"]
cur.execute("""
    INSERT INTO dataset (dataset_id, dataset_name, source_id, methodology, schema_version, created_at, status)
    VALUES (?, ?, ?, ?, ?, ?, ?)
""", (ds["dataset_id"], ds["dataset_name"], ds["source_id"], ds["methodology"], ds["schema_version"], now_str, ds["status"]))

# Register Geography
geo = data["geography"]
cur.execute("""
    INSERT INTO geography (geo_id, place_name, lat, lon, crs, notes)
    VALUES (?, ?, ?, ?, ?, ?)
""", (geo["geo_id"], geo["place_name"], geo["lat"], geo["lon"], geo["crs"], geo["notes"]))

# Register Observation
obs = data["observation"]
cur.execute("""
    INSERT INTO observation (observation_id, dataset_id, geo_id, observation_date, date_precision, species, observation_type, confidence, conflict_flag, conflict_notes, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (obs["observation_id"], obs["dataset_id"], obs["geo_id"], obs["observation_date"], obs["date_precision"], obs["species"], obs["observation_type"], obs["confidence"], int(obs["conflict_flag"]), obs["conflict_notes"], now_str))

# Register Measurement
meas = data["measurement"]
cur.execute("""
    INSERT INTO measurement (measurement_id, observation_id, metric_name, value, unit, method, original_value_text, transform_applied, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (meas["measurement_id"], meas["observation_id"], meas["metric_name"], meas["value"], meas["unit"], meas["method"], meas["original_value_text"], meas["transform_applied"], now_str))

# Register Processing Run
run = data["processing_run"]
cur.execute("""
    INSERT INTO processing_run (run_id, source_id, dataset_id, pipeline_stage, status, input_ref, output_ref, error_detail, started_at, actor)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (run["run_id"], run["source_id"], run["dataset_id"], run["pipeline_stage"], run["status"], run["input_ref"], run["output_ref"], run["error_detail"], now_str, run["actor"]))

# Register Provenance
prov = data["provenance"]
cur.execute("""
    INSERT INTO provenance (provenance_id, measurement_id, source_id, run_id, derivation_note, recorded_at)
    VALUES (?, ?, ?, ?, ?, ?)
""", (prov["provenance_id"], prov["measurement_id"], prov["source_id"], prov["run_id"], prov["derivation_note"], now_str))

conn.commit()
print(f"[2] Ingested corrected baseline record: {meas['measurement_id']} for observation {obs['observation_id']}")

# 3. QUERY AND RETRIEVE TO VERIFY ACCORDING TO ACCEPTANCE CHAINS
cur.execute("""
    SELECT 
        o.observation_id,
        o.date_precision,
        m.measurement_id,
        m.original_value_text,
        m.value,
        m.unit,
        s.source_id,
        s.title,
        r.run_id,
        r.actor,
        p.provenance_id,
        p.derivation_note,
        d.status
    FROM measurement m
    JOIN observation o ON o.observation_id = m.observation_id
    JOIN dataset d ON d.dataset_id = o.dataset_id
    JOIN source s ON s.source_id = d.source_id
    JOIN provenance p ON p.measurement_id = m.measurement_id
    LEFT JOIN processing_run r ON r.run_id = p.run_id
    WHERE m.measurement_id = ?
""", (meas["measurement_id"],))

row = cur.fetchone()
print("\n[3] Acceptance Chain Retrieval Audit:")
print(f"    - Observation ID:       {row[0]} (Precision: {row[1]})")
print(f"    - Measurement ID:       {row[2]}")
print(f"    - Raw Value Extracted:  {row[3]}")
print(f"    - Normalised Value:     {row[4]} {row[5]}")
print(f"    - Source Registry ID:   {row[6]} ('{row[7]}')")
print(f"    - Samachar Run ID:      {row[8]} (Operator: {row[9]})")
print(f"    - Provenance ID:        {row[10]}")
print(f"    - Derivation Note:      {row[11]}")
print(f"    - Validation Status:    {row[12]}")

# 4. IDEMPOTENT RE-INGESTION CHECK (BUG FIXED)
before_count = cur.execute("SELECT COUNT(*) FROM measurement WHERE measurement_id = ?", (meas["measurement_id"],)).fetchone()[0]

# Attempt idempotent insert using the deterministic measurement ID
cur.execute("""
    INSERT INTO measurement (measurement_id, observation_id, metric_name, value, unit, method, original_value_text, transform_applied, created_at)
    SELECT ?, ?, ?, ?, ?, ?, ?, ?, ?
    WHERE NOT EXISTS (SELECT 1 FROM measurement WHERE measurement_id = ?)
""", (meas["measurement_id"], meas["observation_id"], meas["metric_name"], meas["value"], meas["unit"], meas["method"], meas["original_value_text"], meas["transform_applied"], now_str, meas["measurement_id"]))
conn.commit()

after_count = cur.execute("SELECT COUNT(*) FROM measurement WHERE measurement_id = ?", (meas["measurement_id"],)).fetchone()[0]
print(f"\n[4] Idempotency Dedup Test: Ingest count before = {before_count}, after = {after_count} (Expected: 1 -> 1, Row Count remains unchanged)")

# 5. CONSTRAINT VIOLATION CHECK (REJECTION TEST)
invalid_row_rejected = False
try:
    # Attempting to insert observation with invalid date_precision
    cur.execute("""
        INSERT INTO observation (observation_id, dataset_id, geo_id, observation_date, date_precision, species, observation_type, confidence, conflict_flag, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, ("OBS-INVALID-DATE", ds["dataset_id"], geo["geo_id"], "2020-01-01", "INVALID_PRECISION", "Mangrove", "EXTENT", "HIGH", 0, now_str))
    conn.commit()
except sqlite3.IntegrityError as e:
    conn.rollback()
    invalid_row_rejected = True
    print(f"[5] Constraint Validation Test: Succeeded. Rejection error caught: {e}")

if not invalid_row_rejected:
    print("[5] Constraint Validation Test: FAILED. Row was not rejected!")

conn.close()
print("\nVerification execution complete. Output database: vana_demo_corrected.db")
