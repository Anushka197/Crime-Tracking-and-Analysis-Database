import os
import time
import psycopg2
from dotenv import load_dotenv

# Load your secure credentials from the .env file
load_dotenv()

print("Connecting to the Crime Intelligence Database...")
conn = psycopg2.connect(
    host="localhost", # Using localhost since you are running this from your host machine
    port=os.getenv("DB_PORT", 5432),
    dbname=os.getenv("POSTGRES_DB"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD")
)
cursor = conn.cursor()

# The strict 6-level hierarchy to prevent Foreign Key crashes
tables_in_order = [
    "Address",
    "Person", "Evidence",
    "Police_Officer", "Criminal", "Suspect", "Victim", "Witness",
    "Case_Details",
    "Trial", "Collected_For", "Testifies_In", "Assigned_To", "Affected_By", "Involved_In", "Punishment",
    "Linked_to", "Pointed_to"
]

start_time = time.time()

for table in tables_in_order:
    file_path = os.path.join(os.path.dirname(__file__), f"output_data/{table.lower()}.csv")
    print(f"Loading {table}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        # copy_expert bypasses standard SQL inserts and pipes the CSV directly into the DB.
        # WITH CSV NULL AS '' fixes the empty date/boolean crash perfectly!
        copy_sql = f"COPY {table} FROM STDIN WITH CSV NULL AS ''"
        cursor.copy_expert(copy_sql, f)
    
    conn.commit()
    print(f"  ✅ {table} loaded successfully!")

cursor.close()
conn.close()

print(f"\n🎉 Phase 1 Complete! Millions of rows loaded in {round(time.time() - start_time, 2)} seconds.")