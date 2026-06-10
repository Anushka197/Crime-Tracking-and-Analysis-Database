import csv
import random
import time
from datetime import datetime, timedelta
import os
from faker import Faker

fake = Faker()
Faker.seed(42)
random.seed(42)

# ============================================================================
# 1. BIG DATA CONFIGURATION
# ============================================================================
OUTPUT_DIR = "output_data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

TARGETS = {
    'address': 200_000,
    'person': 2_500_000,  
    'police': 50_000,
    'criminal': 100_000,
    'suspect': 350_000,
    'victim': 800_000,
    'witness': 1_200_000,
    'case_details': 1_500_000,
    'evidence': 3_000_000,
    
    # Bridge Tables
    'assigned_to': 500_000,
    'affected_by': 1_000_000,
    'testifies_in': 1_500_000,
    'involved_in': 1_000_000,
    'linked_to': 5_000_000,
    'pointed_to': 4_000_000
}

# ============================================================================
# 2. HYPER-OPTIMIZED CACHES (Bypassing Faker for Speed)
# ============================================================================
print("Warming up hyper-optimized memory pools...")

# Math-based Role Assignment
def get_random_role_id(divisor):
    max_multiplier = TARGETS['person'] // divisor
    return random.randint(1, max_multiplier) * divisor

# Pre-computed Strings
CRIME_TYPES = ['Theft', 'Assault', 'Fraud', 'Cybercrime', 'Homicide', 'Narcotics']
ARREST_STATUS = ['Arrested', 'At Large', 'Released on Bail', 'Cleared']
GENDERS = ['M', 'F', 'O']
COURTS = ['District Court', 'High Court', 'Supreme Court']
descriptions = [fake.sentence(nb_words=6) for _ in range(1000)]
jobs = [fake.job() for _ in range(500)]
names = [fake.first_name() for _ in range(1000)]
last_names = [fake.last_name() for _ in range(1000)]
cities = [fake.city() for _ in range(500)]

# Ultra-Fast Date Generator
base_date = datetime(2020, 1, 1)
def get_fast_dates():
    open_date = base_date + timedelta(days=random.randint(0, 1800))
    crime_date = open_date - timedelta(days=random.randint(0, 30))
    return open_date.strftime('%Y-%m-%d'), crime_date.strftime('%Y-%m-%d')

def get_fast_dob():
    return (base_date - timedelta(days=random.randint(6500, 25000))).strftime('%Y-%m-%d')

# Primary Key Memory Maps
case_dates = [None] * (TARGETS['case_details'] + 1)
evidence_to_case = [None] * (TARGETS['evidence'] + 1)
testifies_pool = [] 

# ============================================================================
# 3. GENERATORS
# ============================================================================

def generate_entities():
    print("Generating Addresses, Persons, and Roles... (This will take a moment)")
    
    with open(f'{OUTPUT_DIR}/address.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        for i in range(1, TARGETS['address'] + 1):
            writer.writerow([i, f"{random.randint(10,999)} {random.choice(last_names)} St", random.choice(cities), "CA", "90210", "USA"])

    with open(f'{OUTPUT_DIR}/person.csv', 'w', newline='', encoding='utf-8') as f_p, \
         open(f'{OUTPUT_DIR}/police_officer.csv', 'w', newline='') as f_pol, \
         open(f'{OUTPUT_DIR}/suspect.csv', 'w', newline='') as f_sus, \
         open(f'{OUTPUT_DIR}/victim.csv', 'w', newline='') as f_vic, \
         open(f'{OUTPUT_DIR}/witness.csv', 'w', newline='') as f_wit:
        
        p_writer, pol_writer, sus_writer, vic_writer, wit_writer = csv.writer(f_p), csv.writer(f_pol), csv.writer(f_sus), csv.writer(f_vic), csv.writer(f_wit)
        
        for i in range(1, TARGETS['person'] + 1):
            p_writer.writerow([
                i, random.choice(GENDERS), get_fast_dob(), random.choice(names), random.choice(names), random.choice(last_names), 
                random.randint(1, TARGETS['address']), random.choice(jobs), "555-0199", "555-0199", random.choice(descriptions)
            ])
            
            if i % 20 == 0: pol_writer.writerow([i, "Officer", "General"])
            if i % 7 == 0:  sus_writer.writerow([i, random.choice(ARREST_STATUS)])
            if i % 4 == 0:  vic_writer.writerow([i, random.choice(descriptions)])
            if i % 3 == 0:  wit_writer.writerow([i, random.choice(descriptions)])

def generate_cases_and_evidence():
    print("Generating Cases and Evidence...")
    with open(f'{OUTPUT_DIR}/case_details.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        for i in range(1, TARGETS['case_details'] + 1):
            open_d, crime_d = get_fast_dates()
            case_dates[i] = open_d 
            
            writer.writerow([
                i, open_d, crime_d, None, random.choice(descriptions),
                random.choice(CRIME_TYPES), random.randint(1, TARGETS['address']),
                random.choice(['Open', 'Closed']), random.randint(1, TARGETS['person'])
            ])

    with open(f'{OUTPUT_DIR}/evidence.csv', 'w', newline='') as f_ev, open(f'{OUTPUT_DIR}/collected_for.csv', 'w', newline='') as f_cf:
        ev_writer, cf_writer = csv.writer(f_ev), csv.writer(f_cf)
        for ev_id in range(1, TARGETS['evidence'] + 1):
            ev_writer.writerow([ev_id, random.choice(descriptions), get_fast_dates()[0], random.randint(1, TARGETS['address'])])
            case_id = random.randint(1, TARGETS['case_details'])
            evidence_to_case[ev_id] = case_id 
            cf_writer.writerow([ev_id, case_id, case_dates[case_id]])

def generate_bridge_tables():
    print("Generating Millions of Bridge Table Connections...")
    
    assigned_set, affected_set, involved_set = set(), set(), set()
    testifies_set, linked_set, pointed_set = set(), set(), set()
    convicted_suspects = set() 

    with open(f'{OUTPUT_DIR}/assigned_to.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        while len(assigned_set) < TARGETS['assigned_to']:
            c_id = random.randint(1, TARGETS['case_details'])
            p_id = get_random_role_id(20)
            if (p_id, c_id) not in assigned_set:
                assigned_set.add((p_id, c_id))
                writer.writerow([p_id, c_id, case_dates[c_id]])

    with open(f'{OUTPUT_DIR}/affected_by.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        while len(affected_set) < TARGETS['affected_by']:
            c_id = random.randint(1, TARGETS['case_details'])
            v_id = get_random_role_id(4)
            if (v_id, c_id) not in affected_set:
                affected_set.add((v_id, c_id))
                writer.writerow([v_id, c_id, case_dates[c_id]])

    with open(f'{OUTPUT_DIR}/testifies_in.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        while len(testifies_set) < TARGETS['testifies_in']:
            c_id = random.randint(1, TARGETS['case_details'])
            w_id = get_random_role_id(3) 
            if (c_id, w_id) not in testifies_set:
                testifies_set.add((c_id, w_id))
                testifies_pool.append((c_id, w_id))
                writer.writerow([c_id, case_dates[c_id], w_id])

    with open(f'{OUTPUT_DIR}/pointed_to.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        while len(pointed_set) < TARGETS['pointed_to']:
            c_id, w_id = random.choice(testifies_pool) 
            s_id = get_random_role_id(7)
            if (c_id, s_id, w_id) not in pointed_set:
                pointed_set.add((c_id, s_id, w_id))
                writer.writerow([c_id, case_dates[c_id], s_id, w_id])

    with open(f'{OUTPUT_DIR}/linked_to.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        while len(linked_set) < TARGETS['linked_to']:
            ev_id = random.randint(1, TARGETS['evidence'])
            c_id = evidence_to_case[ev_id]
            s_id = get_random_role_id(7)
            if (c_id, s_id, ev_id) not in linked_set:
                linked_set.add((c_id, s_id, ev_id))
                writer.writerow([c_id, case_dates[c_id], s_id, ev_id])

    with open(f'{OUTPUT_DIR}/involved_in.csv', 'w', newline='') as f_inv, \
         open(f'{OUTPUT_DIR}/criminal.csv', 'w', newline='') as f_crim, \
         open(f'{OUTPUT_DIR}/punishment.csv', 'w', newline='') as f_pun:
        
        inv_writer, crim_writer, pun_writer = csv.writer(f_inv), csv.writer(f_crim), csv.writer(f_pun)
        
        while len(involved_set) < TARGETS['involved_in']:
            c_id = random.randint(1, TARGETS['case_details'])
            s_id = get_random_role_id(7)
            
            if (c_id, s_id) not in involved_set:
                involved_set.add((c_id, s_id))
                inv_writer.writerow([c_id, case_dates[c_id], s_id])
                
                if random.random() < 0.30:
                    if s_id not in convicted_suspects:
                        convicted_suspects.add(s_id)
                        crim_writer.writerow([s_id, random.choice(ARREST_STATUS)])
                    pun_writer.writerow([s_id, c_id, case_dates[c_id], random.randint(500, 5000), get_fast_dates()[0], None, random.choice(['true', 'false'])])

    with open(f'{OUTPUT_DIR}/trial.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        for case_id in range(1, 2000):
            writer.writerow([case_id, case_dates[case_id], 1, get_fast_dates()[0], random.randint(1, TARGETS['person']), random.choice(COURTS)])

if __name__ == '__main__':
    start = time.time()
    generate_entities()
    generate_cases_and_evidence()
    generate_bridge_tables()
    print(f"✅ Flawless Big Data generation complete in {round(time.time() - start, 2)} seconds!")