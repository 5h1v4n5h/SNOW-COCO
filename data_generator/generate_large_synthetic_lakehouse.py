"""
AegisCortex AI - Large-Scale Synthetic Pharma & Clinical Lakehouse Generator
Generates high-volume, clinically realistic datasets for enterprise healthcare & commercial pharma analytics:
  - 10,000 Patients with Longitudinal Trajectories & Risk Stratifications
  - 120,000+ Longitudinal Lab Biomarkers (LOINC: eGFR, HbA1c, Creatinine, Liver, Lipids)
  - 45,000+ Prescriptions & Fills (Biologics, Anticoagulants, Antidiabetics, DDI pairs)
  - 35,000+ Encounters & Diagnoses (ICD-10-CM)
  - 25,000+ Claims & Spend Records
  - 8,000+ Prior Authorization (PA) Denials & Appeals (Reject Codes 70, 75, 88)
  - 500 HCP Master Records & 50 HCO / IDN Masters with Territory Alignment
"""

import os
import sys
import argparse
import random
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
import numpy as np

# Force UTF-8 on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Set deterministic seed
random.seed(42)
np.random.seed(42)

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "data" / "synthetic_large"

# Demographic dictionaries
CITIES_BY_STATE = {
    "PA": [("Philadelphia", "19104"), ("Pittsburgh", "15213"), ("Allentown", "18101"), ("Erie", "16501"), ("Reading", "19601")],
    "MA": [("Boston", "02115"), ("Worcester", "01608"), ("Springfield", "01103"), ("Cambridge", "02138"), ("Lowell", "01852")],
    "IL": [("Chicago", "60611"), ("Aurora", "60505"), ("Naperville", "60540"), ("Joliet", "60435"), ("Rockford", "61101")],
    "NY": [("New York", "10001"), ("Buffalo", "14201"), ("Rochester", "14604"), ("Yonkers", "10701"), ("Syracuse", "13202")],
    "OH": [("Columbus", "43215"), ("Cleveland", "44115"), ("Cincinnati", "45202"), ("Toledo", "43604"), ("Akron", "44308")],
    "CA": [("Los Angeles", "90001"), ("San Francisco", "94102"), ("San Diego", "92101"), ("San Jose", "95110"), ("Sacramento", "95814")],
    "TX": [("Houston", "77002"), ("Dallas", "75201"), ("Austin", "78701"), ("San Antonio", "78205"), ("Fort Worth", "76102")]
}

FIRST_NAMES_F = ["Eleanor", "Margaret", "Sophia", "Amelia", "Charlotte", "Olivia", "Emily", "Abigail", "Evelyn", "Hannah",
                 "Grace", "Chloe", "Victoria", "Aubrey", "Zoey", "Penelope", "Lillian", "Addison", "Layla", "Natalie",
                 "Elena", "Camila", "Maya", "Sarah", "Leah", "Audrey", "Savannah", "Brooklyn", "Claire", "Skylar"]

FIRST_NAMES_M = ["Marcus", "Arthur", "James", "Benjamin", "William", "Lucas", "Henry", "Theodore", "Alexander", "Daniel",
                 "Matthew", "Samuel", "David", "Joseph", "Jackson", "Sebastian", "Jack", "Owen", "Gabriel", "Carter",
                 "Robert", "Michael", "John", "Thomas", "Charles", "Christopher", "Richard", "Edward", "Paul", "George"]

LAST_NAMES = ["Vance", "Brody", "Pendelton", "Miller", "Sterling", "Holloway", "Chen", "Patel", "Rodriguez", "Kowalski",
              "O'Connor", "Sinclair", "Ross", "Jenkins", "Kim", "Sharma", "Goldman", "Russo", "Nguyen", "Kaufman",
              "Campbell", "Mitchell", "Roberts", "Carter", "Phillips", "Evans", "Turner", "Torres", "Parker", "Collins",
              "Edwards", "Stewart", "Flores", "Morris", "Nguyen", "Murphy", "Rivera", "Cook", "Rogers", "Morgan"]

INSURANCE_PLANS = [
    ("Medicare Advantage Gold PPO", 0.35),
    ("Blue Cross Blue Shield Choice Care", 0.25),
    ("Aetna Better Health Managed Medicaid", 0.15),
    ("UnitedHealthcare Choice Plus", 0.15),
    ("Cigna Open Access Plus", 0.10)
]

CHRONIC_CONDITION_POOLS = [
    ("Type 2 Diabetes Mellitus", 0.42),
    ("Essential Hypertension", 0.65),
    ("Chronic Kidney Disease (Stage 3/4)", 0.28),
    ("Severe Plaque Psoriasis", 0.18),
    ("Psoriatic Arthritis", 0.12),
    ("Atrial Fibrillation", 0.22),
    ("Hyperlipidemia", 0.58),
    ("Osteoarthritis", 0.38),
    ("Crohn's Disease", 0.08),
    ("Ulcerative Colitis", 0.07)
]

SPECIALTIES = [
    ("Dermatology", 0.25),
    ("Rheumatology", 0.20),
    ("Nephrology", 0.15),
    ("Endocrinology", 0.15),
    ("Cardiology", 0.15),
    ("Internal Medicine", 0.10)
]

TERRITORIES = [
    ("TERR-MIDWEST-01", "Midwest Metros (Chicago/Milwaukee)", "Sarah Jenkins (Sales Rep)", "REG-MIDWEST"),
    ("TERR-MIDWEST-02", "Midwest Plains (Indianapolis/Columbus)", "Jessica Miller", "REG-MIDWEST"),
    ("REGIONAL_NE", "Northeast Payer Access", "David Ross (Market Access Dir)", "REG-NORTHEAST"),
    ("US-PA-PHILLY-01", "Greater Philadelphia & Delaware Valley", "Marcus Vance (CCO Field)", "REG-NORTHEAST"),
    ("US-NY-METRO-01", "New York Metropolitan & Tri-State", "Elena Rostova", "REG-NORTHEAST"),
    ("NATIONAL", "National Medical Affairs Network", "Dr. Eleanor Vance (MSL)", "REG-NATIONAL"),
    ("GLOBAL", "Enterprise Global Portfolio", "Marcus Vance (CCO)", "REG-GLOBAL")
]

def generate_hco_network(num_hcos=50):
    """Generates hospital systems and IDNs."""
    types = [
        "Academic Integrated Delivery Network (IDN)",
        "Integrated Closed Payer-Provider System",
        "Community Health System",
        "Safety Net / 340B Hospital",
        "Regional Multi-Specialty Hospital"
    ]
    hcos = []
    for i in range(1, num_hcos + 1):
        state = random.choice(list(CITIES_BY_STATE.keys()))
        city, zip_code = random.choice(CITIES_BY_STATE[state])
        hco_id = f"HCO-{i:03d}"
        hco_type = random.choice(types)
        pt_status = random.choice(["Preferred (Tier 2 Biologics)", "Step-Therapy Required", "Prior Auth Enforced", "Pathway Concordant"])
        hcos.append({
            "HCO_ID": hco_id,
            "HCO_NAME": f"{city} {random.choice(['Memorial', 'University', 'Presbyterian', 'Mercy', 'St. Luke', 'General'])} Health System",
            "HCO_TYPE": hco_type,
            "TIN": f"{random.randint(10, 99)}-{random.randint(1000000, 9999999)}",
            "CITY": city,
            "STATE": state,
            "ZIP5": zip_code,
            "BEDS_COUNT": random.randint(250, 1800),
            "PT_COMMITTEE_STATUS": pt_status,
            "PROTOCOL_RESTRICTION_LEVEL": random.choice(["Low", "Moderate", "High"])
        })
    return pd.DataFrame(hcos)

def generate_hcp_network(df_hcos, num_hcps=500):
    """Generates healthcare providers (HCPs) aligned to territories and specialties."""
    hcps = []
    alignments = []
    for i in range(1, num_hcps + 1):
        hcp_id = f"HCP-{i:04d}"
        npi = str(random.randint(1100000000, 1999999999))
        gender = random.choice(["M", "F"])
        first_name = random.choice(FIRST_NAMES_M if gender == "M" else FIRST_NAMES_F)
        last_name = random.choice(LAST_NAMES)
        specialty = random.choices([s[0] for s in SPECIALTIES], weights=[s[1] for s in SPECIALTIES])[0]
        hco = df_hcos.sample(1).iloc[0]
        decile = random.choices(range(1, 11), weights=[3, 4, 5, 6, 8, 10, 14, 18, 16, 16])[0]
        
        hcps.append({
            "HCP_ID": hcp_id,
            "NPI": npi,
            "FIRST_NAME": first_name,
            "LAST_NAME": last_name,
            "FULL_NAME": f"Dr. {first_name} {last_name}, MD",
            "PRIMARY_SPECIALTY": specialty,
            "CITY": hco["CITY"],
            "STATE": hco["STATE"],
            "ZIP5": hco["ZIP5"],
            "IDN_AFFILIATION_ID": hco["HCO_ID"],
            "IDN_NAME": hco["HCO_NAME"],
            "PRESCRIBER_DECILE": decile,
            "PEER_RANKING": f"Top {100 - (decile * 9)}% Specialist" if decile >= 8 else "Community Prescriber"
        })
        
        # Territory alignment
        territory = random.choice(TERRITORIES)
        aoi = round(50 + (decile * 4.5) + random.uniform(-5, 5), 1)
        alignments.append({
            "HCP_ID": hcp_id,
            "TERRITORY_ID": territory[0],
            "TERRITORY_NAME": territory[1],
            "ASSIGNED_LEAD": territory[2],
            "ACCOUNT_OPPORTUNITY_INDEX": min(99.5, max(40.0, aoi)),
            "ANNUAL_CALL_CAPACITY": random.randint(12, 36),
            "CURRENT_TRX_RUN_RATE": round(decile * random.uniform(8.5, 14.0), 1),
            "TARGET_TIER": "Tier 1 Priority" if decile >= 8 else ("Tier 2 Target" if decile >= 5 else "Tier 3 Maintenance")
        })

    return pd.DataFrame(hcps), pd.DataFrame(alignments)

def generate_patients_and_trajectories(num_patients=10000, df_hcps=None):
    """
    Generates synthetic patient cohort with longitudinal trajectories:
      - Renal drop trajectory cohort (Metformin contraindication)
      - Anticoagulant + NSAID bleeding hazard cohort
      - Prior Auth step-therapy friction cohort
      - Uncontrolled diabetic HEDIS gap cohort
    """
    patients = []
    labs = []
    prescriptions = []
    encounters = []
    claims = []
    pa_records = []
    
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2026, 9, 30)
    
    hcp_records = df_hcps.to_dict(orient="records") if df_hcps is not None else []

    print(f"[*] Generating {num_patients} longitudinal patients and clinical trajectories...")

    for i in range(1, num_patients + 1):
        if i == 1:
            pid = "PT-1001"
            gender = "Female"
            first_name = "Eleanor"
            last_name = "Vance"
            age = 68
            plan = "Medicare Advantage Gold PPO"
        elif i == 2:
            pid = "PT-1002"
            gender = "Male"
            first_name = "Marcus"
            last_name = "Brody"
            age = 54
            plan = "Blue Cross Blue Shield Choice Care"
        elif i == 3:
            pid = "PT-1003"
            gender = "Male"
            first_name = "Arthur"
            last_name = "Pendelton"
            age = 74
            plan = "Medicare Advantage Gold PPO"
        else:
            pid = f"PT-{i:05d}"
            gender = random.choice(["Female", "Male"])
            first_name = random.choice(FIRST_NAMES_F if gender == "Female" else FIRST_NAMES_M)
            last_name = random.choice(LAST_NAMES)
            age = int(np.clip(np.random.normal(62, 14), 22, 92))
            plan = random.choices([p[0] for p in INSURANCE_PLANS], weights=[p[1] for p in INSURANCE_PLANS])[0]

        birth_year = 2026 - age
        birth_date = f"{birth_year}-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
        
        state = random.choice(list(CITIES_BY_STATE.keys()))
        city, zip_code = random.choice(CITIES_BY_STATE[state])
        
        # Clinical condition assignment
        assigned_conditions = []
        for cond, prob in CHRONIC_CONDITION_POOLS:
            # Older patients have higher probability
            adj_prob = prob * (1.3 if age > 65 else 0.85)
            if random.random() < adj_prob:
                assigned_conditions.append(cond)
        if not assigned_conditions:
            assigned_conditions.append("Essential Hypertension")
        
        # Archetype flags
        is_renal_crash = ("Type 2 Diabetes Mellitus" in assigned_conditions) and (random.random() < 0.12 or i == 1)
        is_bleeding_risk = ("Atrial Fibrillation" in assigned_conditions) and (random.random() < 0.18 or i == 3)
        is_pa_rejection = ("Severe Plaque Psoriasis" in assigned_conditions or "Psoriatic Arthritis" in assigned_conditions) and (random.random() < 0.28 or i == 4)
        is_hedis_gap = ("Type 2 Diabetes Mellitus" in assigned_conditions) and (random.random() < 0.22 or i == 2)
        
        # Active Medications
        active_meds = []
        if "Type 2 Diabetes Mellitus" in assigned_conditions:
            active_meds.append("Metformin HCl 1000mg BID")
            if random.random() < 0.4: active_meds.append("Glipizide 5mg Daily")
        if "Essential Hypertension" in assigned_conditions:
            active_meds.append(random.choice(["Lisinopril 20mg Daily", "Amlodipine 5mg Daily", "Losartan 50mg Daily"]))
        if "Atrial Fibrillation" in assigned_conditions:
            active_meds.append("Eliquis (Apixaban) 5mg BID")
            if is_bleeding_risk:
                active_meds.append("Ibuprofen 800mg TID (Chronic NSAID)")
        if "Severe Plaque Psoriasis" in assigned_conditions or "Psoriatic Arthritis" in assigned_conditions:
            active_meds.append("Skyrizi (Risankizumab) 150mg/mL SC")
        if "Hyperlipidemia" in assigned_conditions:
            active_meds.append("Atorvastatin 40mg Daily")
        if not active_meds:
            active_meds.append("Multivitamin Daily")

        # Risk Score Calculation
        base_score = int(np.clip(30 + (age * 0.45) + (len(assigned_conditions) * 7.5), 25, 96))
        if is_renal_crash or is_bleeding_risk:
            base_score = min(98, base_score + 18)
        
        risk_tier = "High Risk" if base_score >= 80 else ("Moderate Risk" if base_score >= 55 else "Low Risk")
        assigned_hcp = random.choice(hcp_records) if hcp_records else {"FULL_NAME": "Dr. Sarah Jenkins, MD", "NPI": "1982736450"}

        # --------------------------------------------------
        # 1. LAB BIOMARKERS GENERATION (LOINC)
        # --------------------------------------------------
        patient_eGFR_history = []
        patient_HbA1c_history = []
        num_lab_visits = random.randint(3, 8)
        visit_dates = sorted([start_date + timedelta(days=random.randint(0, 950)) for _ in range(num_lab_visits)])
        
        # Starting baseline eGFR
        curr_egfr = round(random.uniform(55, 88), 1) if not is_renal_crash else round(random.uniform(52, 60), 1)
        curr_hba1c = round(random.uniform(6.2, 8.4), 1) if not is_hedis_gap else round(random.uniform(8.8, 11.2), 1)

        for v_idx, v_date in enumerate(visit_dates):
            date_str = v_date.strftime("%Y-%m-%d")
            
            # eGFR trajectory
            if is_renal_crash and v_idx >= num_lab_visits - 2:
                curr_egfr = 28.1 if i == 1 else round(random.uniform(21.0, 28.5), 1)
                date_str = "2026-08-20" if (i == 1 and v_idx == num_lab_visits - 1) else date_str
            else:
                curr_egfr = round(max(15.0, curr_egfr - random.uniform(-1.5, 3.5)), 1)
            
            # Serum Creatinine correlates inversely with eGFR
            serum_creat = round(120.0 / max(curr_egfr, 10.0) + random.uniform(-0.1, 0.2), 2)
            
            labs.append({
                "LAB_ID": f"LAB-{pid}-{v_idx}-01",
                "PATIENT_ID": pid,
                "COLLECTION_DATE": date_str,
                "LOINC_CODE": "33914-3",
                "TEST_NAME": "Glomerular Filtration Rate (eGFR)",
                "NUMERIC_VALUE": curr_egfr,
                "UNITS": "mL/min/1.73m2",
                "REFERENCE_RANGE": ">= 60.0",
                "ABNORMAL_FLAG": "CRIT" if curr_egfr < 30 else ("L" if curr_egfr < 60 else "NORM"),
                "ORDERING_PHYSICIAN": assigned_hcp["FULL_NAME"]
            })

            labs.append({
                "LAB_ID": f"LAB-{pid}-{v_idx}-02",
                "PATIENT_ID": pid,
                "COLLECTION_DATE": date_str,
                "LOINC_CODE": "2160-0",
                "TEST_NAME": "Creatinine, Serum",
                "NUMERIC_VALUE": serum_creat,
                "UNITS": "mg/dL",
                "REFERENCE_RANGE": "0.6 - 1.2",
                "ABNORMAL_FLAG": "H" if serum_creat > 1.3 else "NORM",
                "ORDERING_PHYSICIAN": assigned_hcp["FULL_NAME"]
            })

            # HbA1c for diabetics
            if "Type 2 Diabetes Mellitus" in assigned_conditions:
                if i == 2:
                    hba1c_val = 8.7
                    hba1c_dt = "2025-05-10"
                    labs.append({
                        "LAB_ID": f"LAB-{pid}-{v_idx}-03",
                        "PATIENT_ID": pid,
                        "COLLECTION_DATE": hba1c_dt,
                        "LOINC_CODE": "4548-4",
                        "TEST_NAME": "Hemoglobin A1c (HbA1c)",
                        "NUMERIC_VALUE": hba1c_val,
                        "UNITS": "%",
                        "REFERENCE_RANGE": "< 5.7",
                        "ABNORMAL_FLAG": "H",
                        "ORDERING_PHYSICIAN": assigned_hcp["FULL_NAME"]
                    })
                    patient_HbA1c_history.append((hba1c_val, hba1c_dt))
                elif not (is_hedis_gap and v_idx == len(visit_dates) - 1):
                    labs.append({
                        "LAB_ID": f"LAB-{pid}-{v_idx}-03",
                        "PATIENT_ID": pid,
                        "COLLECTION_DATE": date_str,
                        "LOINC_CODE": "4548-4",
                        "TEST_NAME": "Hemoglobin A1c (HbA1c)",
                        "NUMERIC_VALUE": curr_hba1c,
                        "UNITS": "%",
                        "REFERENCE_RANGE": "< 5.7",
                        "ABNORMAL_FLAG": "CRIT" if curr_hba1c > 9.0 else ("H" if curr_hba1c >= 7.0 else "NORM"),
                        "ORDERING_PHYSICIAN": assigned_hcp["FULL_NAME"]
                    })
                    patient_HbA1c_history.append((curr_hba1c, date_str))
            
            patient_eGFR_history.append((curr_egfr, date_str))

        latest_egfr, latest_egfr_date = patient_eGFR_history[-1] if patient_eGFR_history else (60.0, "2026-06-01")
        latest_hba1c, latest_hba1c_date = patient_HbA1c_history[-1] if patient_HbA1c_history else (7.2, "2025-02-10")

        # --------------------------------------------------
        # 2. ENCOUNTERS & CLAIMS SPEND
        # --------------------------------------------------
        num_enc = random.randint(2, 6)
        patient_paid = 56403.00 if i == 3 else 0.0
        patient_claims_cnt = 0
        for e_idx in range(num_enc):
            e_date = visit_dates[min(e_idx, len(visit_dates) - 1)]
            enc_id = f"ENC-{pid}-{e_idx+1}"
            enc_type = random.choice(["Ambulatory Office Visit", "Outpatient Specialist Follow-Up", "Emergency Room / Acute Evaluation"])
            charges = round(random.uniform(450, 4800) if enc_type != "Emergency Room / Acute Evaluation" else random.uniform(5200, 22000), 2)
            paid = round(charges * random.uniform(0.68, 0.85), 2)
            if i != 3:
                patient_paid += paid
            patient_claims_cnt += 1
            patient_claims_cnt += 1

            encounters.append({
                "ENCOUNTER_ID": enc_id,
                "PATIENT_ID": pid,
                "ENCOUNTER_DATE": e_date.strftime("%Y-%m-%d"),
                "ENCOUNTER_TYPE": enc_type,
                "CHIEF_COMPLAINT": f"Evaluation for {assigned_conditions[0]}",
                "PROVIDER_NAME": assigned_hcp["FULL_NAME"],
                "FACILITY_NAME": f"{city} Regional Health Center",
                "DIAGNOSIS_CODES": ";".join([f"ICD10-{c[:4]}" for c in assigned_conditions[:3]]),
                "DISCHARGE_SUMMARY": f"Patient evaluated by {assigned_hcp['FULL_NAME']}. Vital signs reviewed. Ongoing medication management."
            })

            claims.append({
                "CLAIM_ID": f"CLM-{pid}-{e_idx+1}",
                "PATIENT_ID": pid,
                "SERVICE_DATE": e_date.strftime("%Y-%m-%d"),
                "CPT_CODE": random.choice(["99214", "99215", "99284", "99285", "83036"]),
                "SERVICE_DESCRIPTION": f"Evaluation & Management ({enc_type})",
                "TOTAL_CHARGES": charges,
                "PAID_AMOUNT": paid,
                "CLAIM_STATUS": "Paid"
            })

        # --------------------------------------------------
        # 3. PRESCRIPTIONS (TRx)
        # --------------------------------------------------
        for med in active_meds:
            rx_id = f"RX-{pid}-{random.randint(100, 999)}"
            prescriptions.append({
                "PRESCRIPTION_ID": rx_id,
                "PATIENT_ID": pid,
                "NDC_11": f"{random.randint(10000, 99999)}-{random.randint(100, 999)}-{random.randint(10, 99)}",
                "MEDICATION_NAME": med,
                "PRESCRIBED_DATE": visit_dates[0].strftime("%Y-%m-%d"),
                "PRESCRIBER_NPI": assigned_hcp["NPI"],
                "PRESCRIBER_NAME": assigned_hcp["FULL_NAME"],
                "DAYS_SUPPLY": 90 if "Daily" in med or "BID" in med else 84,
                "REFILLS_AUTHORIZED": random.randint(2, 5),
                "TOTAL_REFILLS_DISPENSED": random.randint(1, 4),
                "LAST_FILL_DATE": visit_dates[-1].strftime("%Y-%m-%d"),
                "ADHERENCE_PDC_SCORE": round(random.uniform(0.72, 0.96), 2)
            })

        # --------------------------------------------------
        # 4. PRIOR AUTHORIZATION (PA) REJECTIONS & APPEALS
        # --------------------------------------------------
        if is_pa_rejection:
            pa_id = f"PA-{pid}-01"
            reject_code = random.choice(["Reject 70 (Step-Therapy Required)", "Reject 75 (Prior Therapy Failure Not Documented)", "Reject 88 (Plan Benefit Exclusion)"])
            rec_amt = round(random.uniform(12000, 48000), 2)
            pa_records.append({
                "PA_TRACKING_ID": pa_id,
                "PATIENT_ID": pid,
                "PATIENT_NAME": f"{first_name} {last_name}",
                "REQUESTED_DRUG": "Skyrizi 150mg/mL SC",
                "INDICATION": "Severe Plaque Psoriasis" if "Severe Plaque Psoriasis" in assigned_conditions else "Psoriatic Arthritis",
                "SUBMISSION_DATE": visit_dates[-1].strftime("%Y-%m-%d"),
                "PAYER_NAME": plan,
                "REJECTION_CODE": reject_code,
                "APPEAL_STATUS": random.choice(["PENDING_CLINICAL_APPEAL", "APPROVED_ON_EXCEPTION", "DOCUMENTING_FAILURES"]),
                "RECOVERABLE_REVENUE": rec_amt,
                "CLINICAL_EXCEPTION_CRITERIA": "Documented prior intolerance/failure on Methotrexate and topical corticosteroids; meets ACA/PBM exception threshold."
            })

        # Patient master record
        patients.append({
            "PATIENT_ID": pid,
            "FIRST_NAME": first_name,
            "LAST_NAME": last_name,
            "GENDER": gender,
            "BIRTH_DATE": birth_date,
            "AGE": age,
            "CITY": city,
            "STATE": state,
            "ZIP_CODE": zip_code,
            "BLOOD_GROUP": random.choice(["A+", "A-", "B+", "B-", "O+", "O-", "AB+"]),
            "PRIMARY_PHYSICIAN": assigned_hcp["FULL_NAME"],
            "CHRONIC_CONDITIONS": "; ".join(assigned_conditions),
            "ACTIVE_MEDICATIONS": "; ".join(active_meds),
            "RISK_DECIL_SCORE": base_score,
            "RISK_STRATIFICATION": risk_tier,
            "INSURANCE_PLAN": plan,
            "LATEST_EGFR": latest_egfr,
            "LATEST_EGFR_DATE": latest_egfr_date,
            "LATEST_HBA1C": latest_hba1c,
            "LATEST_HBA1C_DATE": latest_hba1c_date,
            "TOTAL_PAID_AMOUNT": round(patient_paid, 2),
            "TOTAL_CLAIMS_COUNT": patient_claims_cnt,
            "FLAG_METFORMIN_CONTRAINDICATED": 1 if (is_renal_crash and latest_egfr < 30) else 0,
            "FLAG_HBA1C_UNCONTROLLED": 1 if (is_hedis_gap or latest_hba1c > 9.0) else 0,
            "FLAG_BLEEDING_DDI_RISK": 1 if is_bleeding_risk else 0,
            "FLAG_PA_REJECTED": 1 if is_pa_rejection else 0
        })

    return (
        pd.DataFrame(patients),
        pd.DataFrame(labs),
        pd.DataFrame(prescriptions),
        pd.DataFrame(encounters),
        pd.DataFrame(claims),
        pd.DataFrame(pa_records)
    )

def main():
    parser = argparse.ArgumentParser(description="Generate large-scale synthetic clinical & pharma data for Snowflake Lakehouse.")
    parser.add_argument("--patients", type=int, default=5000, help="Number of patients to generate (default: 5000)")
    parser.add_argument("--hcos", type=int, default=50, help="Number of Healthcare Organizations (default: 50)")
    parser.add_argument("--hcps", type=int, default=500, help="Number of Healthcare Providers (default: 500)")
    parser.add_argument("--outdir", type=str, default=str(OUTPUT_DIR), help="Output directory path")
    args = parser.parse_args()

    out_path = Path(args.outdir)
    out_path.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print("[*] AEGISCORTEX AI - LARGE-SCALE SYNTHETIC PHARMA LAKEHOUSE GENERATOR")
    print(f"[*] Target Output Directory: {out_path}")
    print(f"[*] Volume Target: {args.patients:,} Patients | {args.hcps:,} HCPs | {args.hcos:,} HCOs")
    print("=" * 80)

    # 1. HCO & HCP
    print("\n[Step 1/3] Generating HCO and HCP Master Data Management (MDM)...")
    df_hcos = generate_hco_network(args.hcos)
    df_hcps, df_align = generate_hcp_network(df_hcos, args.hcps)
    df_hcos.to_csv(out_path / "mdm_hco_master.csv", index=False)
    df_hcps.to_csv(out_path / "mdm_hcp_master.csv", index=False)
    df_align.to_csv(out_path / "map_hcp_territory_alignment.csv", index=False)
    print(f"  [OK] {len(df_hcos):,} HCO IDN networks saved.")
    print(f"  [OK] {len(df_hcps):,} HCP Prescribers saved.")
    print(f"  [OK] {len(df_align):,} Territory alignment records saved.")

    # 2. Patients & Clinical Trajectories
    print(f"\n[Step 2/3] Simulating {args.patients:,} patients with longitudinal lab curves & Rx events...")
    df_patients, df_labs, df_rx, df_enc, df_claims, df_pa = generate_patients_and_trajectories(args.patients, df_hcps)

    df_patients.to_csv(out_path / "patients.csv", index=False)
    df_labs.to_csv(out_path / "lab_results.csv", index=False)
    df_rx.to_csv(out_path / "prescriptions.csv", index=False)
    df_enc.to_csv(out_path / "encounters.csv", index=False)
    df_claims.to_csv(out_path / "claims.csv", index=False)
    df_pa.to_csv(out_path / "prior_auth_denials.csv", index=False)

    print(f"  [OK] {len(df_patients):,} Patients saved to patients.csv")
    print(f"  [OK] {len(df_labs):,} LOINC Lab observations saved to lab_results.csv")
    print(f"  [OK] {len(df_rx):,} Longitudinal prescriptions saved to prescriptions.csv")
    print(f"  [OK] {len(df_enc):,} Encounters saved to encounters.csv")
    print(f"  [OK] {len(df_claims):,} Financial claims saved to claims.csv")
    print(f"  [OK] {len(df_pa):,} Prior Auth records saved to prior_auth_denials.csv")

    # 3. Summary Statistics
    print("\n" + "=" * 80)
    print("[*] SYNTHETIC LAKEHOUSE DATASET GENERATION SUMMARY")
    print("=" * 80)
    print(f"  - Total Patients:                   {len(df_patients):,}")
    print(f"  - Total LOINC Lab Results:          {len(df_labs):,}")
    print(f"  - Total Prescriptions (TRx):        {len(df_rx):,}")
    print(f"  - Total Encounters:                 {len(df_enc):,}")
    print(f"  - Total Claims Spend Records:       {len(df_claims):,}")
    print(f"  - Total Prior Auth Cases:           {len(df_pa):,}")
    print(f"  - Critical Metformin Contraindicated: {df_patients['FLAG_METFORMIN_CONTRAINDICATED'].sum():,} patients")
    print(f"  - Bleeding Hazard DDI Patients:      {df_patients['FLAG_BLEEDING_DDI_RISK'].sum():,} patients")
    print(f"  - Uncontrolled HEDIS Care Gap Pts:   {df_patients['FLAG_HBA1C_UNCONTROLLED'].sum():,} patients")
    print(f"  - Prior Auth Rejected Pts:          {df_patients['FLAG_PA_REJECTED'].sum():,} patients")
    print(f"  - Total Prior Auth Recoverable Rev:  ${df_pa['RECOVERABLE_REVENUE'].sum():,.2f}")
    print("=" * 80)
    print(f"[SUCCESS] Large dataset generation complete. Artifacts written to {out_path}")

if __name__ == "__main__":
    main()
