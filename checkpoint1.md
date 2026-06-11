# Crime Intelligence System — Checkpoint 1

## Project Goal

Build a large-scale Crime Intelligence and Analytics platform demonstrating relational database design, synthetic data generation at scale, PostgreSQL transactional workloads, Hadoop HDFS data lake storage, Spark-based distributed processing, Parquet optimization, and performance benchmarking.

---

## Overall Plan

| Phase | Description | Status |
|-------|-------------|--------|
| 1 | Transactional System (Schema + Data + PostgreSQL) | Complete |
| 2 | Data Lake Ingestion into HDFS (Bronze Layer) | Complete |
| 3 | Spark Cluster Setup | Pending |
| 4 | CSV → Parquet Transformation (Gold Layer) | Pending |
| 5 | Performance Benchmarking | Pending |

---

## Phase 1: Transactional System

### Database Schema

Designed a normalized PostgreSQL schema for a crime intelligence domain.

**Core entities:** Address, Person, Case_Details, Trial, Evidence

**Role-based entities:** Police_Officer, Criminal, Suspect, Victim, Witness

**Relationship tables:** Assigned_To, Affected_By, Testifies_In, Involved_In, Collected_For, Linked_to, Pointed_to, Punishment

**Key design decisions:**
- Composite primary keys on Case_Details `(case_id, open_date)` to model case history
- Foreign keys enforcing referential integrity across all relationships
- Auth table for application-level user management

### Synthetic Data Generation

`Data_Generator/generate_seed.py` generates millions of rows across all tables.

**Dataset scale:**

| Table | Rows |
|-------|------|
| Address | 200,000 |
| Person | 2,500,000 |
| Case_Details | 1,500,000 |
| Evidence | 3,000,000 |
| Linked_To | 5,000,000 |
| Pointed_To | 4,000,000 |
| Other bridge tables | ~5,000,000 |
| **Total dataset** | **~1.2–1.3 GB CSV** |

**Optimizations used:**
- Pre-generated in-memory pools for names, cities, jobs, and descriptions instead of calling `faker` per row
- Math-based role ID assignment to maintain foreign key consistency without lookup tables
- In-memory maps (`case_dates[]`, `evidence_to_case[]`) to track keys during generation, avoiding re-reads

### PostgreSQL Deployment

Deployed using Docker Compose with `postgres:16-alpine`. Credentials stored in `.env`. Schema auto-initialized by mounting `schema.sql` into `/docker-entrypoint-initdb.d/`.

Verified with `\dt` → **19 tables found.**

### Bulk Data Loading

`Data_Generator/load_data.py` uses PostgreSQL's `COPY ... FROM STDIN WITH CSV` command rather than INSERT statements, which is orders of magnitude faster for millions of rows.

Tables loaded in foreign-key dependency order: Address → Person → Evidence → roles → Case_Details → relationship tables.

---

## Phase 2: Hadoop Data Lake (Bronze Layer)

### Hadoop Deployment

Added `namenode` and `datanode` services to `compose.yaml` using `bde2020/hadoop-namenode` and `bde2020/hadoop-datanode` images.

### Problem Encountered: DataNode Not Connecting

**Symptom:** `hdfs dfs -put` returned `There are 0 datanode(s) running`.

**Root cause:** Each container auto-generated its own hostname, so:
- NameNode advertised `fs.defaultFS=hdfs://<container-id-1>:8020`
- DataNode tried to register with `hdfs://<container-id-2>:8020` (itself)

**Fix:** Pinned an explicit hostname and set `CORE_CONF_fs_defaultFS=hdfs://namenode:9000` on both services so they resolve to the same endpoint.

Cluster was reset with `docker compose down -v` to clear stale metadata, then restarted.

### Verification

```
hdfs dfsadmin -report
→ Live datanodes (1)
→ Configured Capacity: 1006.85 GB
```

### HDFS Ingestion

Created Bronze Layer directory:
```
/crime_data/bronze/raw_csvs
```

CSV files copied from host into the container with `docker cp`, then loaded with `hdfs dfs -put`.

**Result: 18 CSV datasets stored in HDFS.**

**Storage summary (selected files):**

| File | Size |
|------|------|
| person.csv | 301.9 MB |
| evidence.csv | 181.6 MB |
| linked_to.csv | 164.2 MB |
| case_details.csv | 138.8 MB |
| **Total raw** | **~1.2–1.3 GB** |
| **With replication (factor 3)** | **~3.7 GB** |

---

## Results

### HDFS Cluster — Namenode

![Namenode Information](Results/Screenshot%202026-06-11%20192329.png)

### HDFS Cluster — Datanode

![Datanode Information](Results/Screenshot%202026-06-11%20193049.png)

### HDFS Browser — Bronze Layer Files

![Browsing HDFS](Results/Screenshot%202026-06-11%20193435.png)

---

## Current Architecture

```
Host Machine
├── PostgreSQL (Docker)
│   └── Crime Intelligence Schema — 19 tables, ~15M+ rows
├── Data Generator
│   └── 1.2+ GB CSV Dataset
├── Hadoop NameNode (Docker)
├── Hadoop DataNode (Docker)
└── HDFS
    └── /crime_data/bronze/raw_csvs
        ├── person.csv
        ├── evidence.csv
        ├── case_details.csv
        └── ... (18 files total)
```

---

## Key Engineering Challenges Solved

1. **Large-scale data generation** — ~15M+ rows generated efficiently using pre-computed memory pools instead of per-row Faker calls.
2. **Normalized schema with deep FK chains** — Loading order designed to satisfy all foreign key dependencies without errors.
3. **Dockerized PostgreSQL** — Schema auto-initialized on container startup; credentials externalized to `.env`.
4. **Hadoop networking bug** — DataNode was connecting to itself instead of the NameNode due to auto-generated hostnames; fixed with explicit hostname pinning.
5. **HDFS cluster recovery** — Destroyed stale volume metadata and reconfigured from scratch to get a healthy single-node cluster.
6. **Bulk HDFS ingestion** — 1.2 GB of CSV data loaded into the Bronze Layer and verified.
