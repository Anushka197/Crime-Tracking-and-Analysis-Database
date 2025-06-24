# 📁 Crime-Tracking-and-Analysis-Database


A full-fledged database management project designed to model, store, and analyze criminal cases, personnel, legal processes, and evidentiary records. This project simulates a crime investigation management system where complex relationships between suspects, victims, officers, cases, court trials information and evidence are stored and queried efficiently using SQL and relational principles.

---
## 📌 Overview

This project models the lifecycle of a criminal case — from reporting and evidence collection to trials and punishments. Built as part of the DBMS course at DAU, it features:

- A **well-normalized schema** reflecting real-world crime record systems.
- **Functional dependencies and BCNF design** validated for all relations.
- Sample **data population with 50+ records** for realistic querying.
- 14+ insightful SQL queries that reveal patterns, analytics, and critical case details.

---
## 🧩 Key Features

- **Entity-Rich Schema**: Includes `Person`, `Criminal`, `Police_Officer`, `Trial`, `Case_Details`, `Evidence`, and more.
- **Relationship Modeling**: Captures many-to-many relations like suspects involved in multiple cases, witnesses testifying across trials, etc.
- **Conflict-Free Design**: All tables are normalized and satisfy **BCNF** for data consistency and integrity.
- **Powerful Querying Capabilities**:
  - Understand crime patterns
  - Track legal progress
  - Evaluate officer performance
  - Discover data-driven insights from case records

---

## 🧠 Database Design

The relational model was crafted using:

- **Entity-Relationship Diagram**
- **Relational Schema**
- **Functional Dependencies**
- **BCNF Normalization**

Key entities and relationships include:

- Core Entities: `Person`, `Case_Details`, `Trial`, `Evidence`
- Roles: `Victim`, `Criminal`, `Suspect`, `Witness`, `Police Officer`
- Associative Entities: `Testifies_In`, `Assigned_To`, `Collected_For`, `Linked_To`, `Involved_In`, `Affected_By`

---

## 📁 Folder Structure

```plaintext
📦 Crime-Tracking-Database/
├── 📄 table_formation.txt       # SQL script for table creation
├── 📄 Data_Insertion.txt    # Sample data for all major entities
├── 📄 queries.txt           # Analytical and report-style SQL queries
├── 📄 top3Queries.pdf   
```

---

##👥 Team Members
- Manan Chhabhaya
- Kresha Vora
- Anushka Prajapati
- Kashyap Ajudiya
- Jal Khunt
