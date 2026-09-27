"""
AegisCortex AI - Synthetic Clinical Data & Document Generator
Generates realistic, clinically validated EHR, Claims, LOINC Labs, and FDA Reference Inserts.
"""

import os
import csv
import json
import random
from datetime import datetime, timedelta

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
CSV_DIR = os.path.join(DATA_DIR, "raw_csv")
DOCS_DIR = os.path.join(DATA_DIR, "clinical_docs")

os.makedirs(CSV_DIR, exist_ok=True)
os.makedirs(DOCS_DIR, exist_ok=True)

# Fixed seed for deterministic reproducibility
random.seed(42)

# ==============================================================================
# 1. GENERATE PATIENTS
# ==============================================================================

FIRST_NAMES_F = ["Eleanor", "Margaret", "Sophia", "Amelia", "Charlotte", "Olivia", "Emily", "Abigail", "Evelyn", "Hannah"]
FIRST_NAMES_M = ["Marcus", "Arthur", "James", "Benjamin", "William", "Lucas", "Henry", "Theodore", "Alexander", "Daniel"]
LAST_NAMES = ["Vance", "Brody", "Pendelton", "Miller", "Sterling", "Holloway", "Chen", "Patel", "Rodriguez", "Kowalski", "O'Connor", "Sinclair"]

PHYSICIANS = [
    "Dr. Robert Harrison, MD (Internal Medicine)",
    "Dr. Sarah Jenkins, MD (Endocrinology)",
    "Dr. David Kim, MD (Cardiology)",
    "Dr. Maria Gonzalez, MD (Nephrology)",
    "Dr. Anita Sharma, MD (Family Medicine)"
]

def generate_patients():
    patients = []
    
    # HERO 1: Eleanor Vance (PT-1001) - Acute Renal Failure + Metformin Contraindication
    patients.append({
        "PATIENT_ID": "PT-1001",
        "FIRST_NAME": "Eleanor",
        "LAST_NAME": "Vance",
        "GENDER": "Female",
        "BIRTH_DATE": "1958-04-12",
        "AGE": 68,
        "CITY": "Boston",
        "STATE": "MA",
        "ZIP_CODE": "02115",
        "BLOOD_GROUP": "O+",
        "PRIMARY_PHYSICIAN": "Dr. Robert Harrison, MD (Internal Medicine)",
        "CHRONIC_CONDITIONS": "Type 2 Diabetes Mellitus; Hypertension; Chronic Kidney Disease (Stage 3b/4)",
        "ACTIVE_MEDICATIONS": "Metformin 1000mg BID; Lisinopril 20mg Daily; Atorvastatin 40mg Daily",
        "RISK_DECIL_SCORE": 88,
        "RISK_STRATIFICATION": "High Risk",
        "INSURANCE_PLAN": "Medicare Advantage Gold PPO"
    })
    
    # HERO 2: Marcus Brody (PT-1002) - HEDIS Diabetic Care Gap (Overdue HbA1c)
    patients.append({
        "PATIENT_ID": "PT-1002",
        "FIRST_NAME": "Marcus",
        "LAST_NAME": "Brody",
        "GENDER": "Male",
        "BIRTH_DATE": "1972-09-24",
        "AGE": 54,
        "CITY": "Worcester",
        "STATE": "MA",
        "ZIP_CODE": "01608",
        "BLOOD_GROUP": "A+",
        "PRIMARY_PHYSICIAN": "Dr. Sarah Jenkins, MD (Endocrinology)",
        "CHRONIC_CONDITIONS": "Type 2 Diabetes Mellitus; Hyperlipidemia; Mild Obesity",
        "ACTIVE_MEDICATIONS": "Glipizide 10mg Daily; Atorvastatin 20mg Daily; Metformin 500mg Daily",
        "RISK_DECIL_SCORE": 62,
        "RISK_STRATIFICATION": "Moderate Risk",
        "INSURANCE_PLAN": "Blue Cross Blue Shield Commercial Comprehensive"
    })
    
    # HERO 3: Arthur Pendelton (PT-1003) - Polypharmacy & Anticoagulant + NSAID Bleeding Risk
    patients.append({
        "PATIENT_ID": "PT-1003",
        "FIRST_NAME": "Arthur",
        "LAST_NAME": "Pendelton",
        "GENDER": "Male",
        "BIRTH_DATE": "1952-11-03",
        "AGE": 74,
        "CITY": "Cambridge",
        "STATE": "MA",
        "ZIP_CODE": "02138",
        "BLOOD_GROUP": "B-",
        "PRIMARY_PHYSICIAN": "Dr. David Kim, MD (Cardiology)",
        "CHRONIC_CONDITIONS": "Non-valvular Atrial Fibrillation; Congestive Heart Failure; Severe Osteoarthritis; Gastroesophageal Reflux",
        "ACTIVE_MEDICATIONS": "Apixaban 5mg BID; Ibuprofen 800mg TID; Furosemide 40mg Daily; Carvedilol 12.5mg BID; Omeprazole 20mg Daily; Atorvastatin 80mg Daily; Amlodipine 5mg Daily; Gabapentin 300mg TID; Acetaminophen 500mg PRN",
        "RISK_DECIL_SCORE": 94,
        "RISK_STRATIFICATION": "Catastrophic / Top Decile Risk",
        "INSURANCE_PLAN": "Medicare Advantage Premier Dual-Eligible"
    })
    
    # 47 Additional Co-hort Patients
    common_med_groups = [
        "Lisinopril 10mg Daily; Amlodipine 5mg Daily",
        "Levothyroxine 75mcg Daily; Multivitamin",
        "Albuterol Inhaler PRN; Fluticasone Propionate Daily",
        "Sertraline 50mg Daily; Hydrochlorothiazide 25mg Daily",
        "Omeprazole 40mg Daily; Losartan 50mg Daily",
        "Metoprolol Succinate 50mg Daily; Rosuvastatin 10mg Daily"
    ]
    common_conditions = [
        "Essential Hypertension; Hyperlipidemia",
        "Hypothyroidism; Osteopenia",
        "Mild Persistent Asthma; Seasonal Allergic Rhinitis",
        "Major Depressive Disorder (In Remission); Hypertension",
        "GERD; Benign Prostatic Hyperplasia",
        "Coronary Artery Disease; Chronic Stable Angina"
    ]
    
    for i in range(4, 51):
        pid = f"PT-{1000 + i}"
        is_female = random.choice([True, False])
        fn = random.choice(FIRST_NAMES_F if is_female else FIRST_NAMES_M)
        ln = random.choice(LAST_NAMES)
        birth_year = random.randint(1945, 1995)
        age = 2026 - birth_year
        risk_score = random.randint(15, 85)
        risk_strat = "Low Risk" if risk_score < 40 else ("Moderate Risk" if risk_score < 75 else "High Risk")
        
        patients.append({
            "PATIENT_ID": pid,
            "FIRST_NAME": fn,
            "LAST_NAME": ln,
            "GENDER": "Female" if is_female else "Male",
            "BIRTH_DATE": f"{birth_year}-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
            "AGE": age,
            "CITY": random.choice(["Boston", "Cambridge", "Somerville", "Newton", "Quincy", "Waltham"]),
            "STATE": "MA",
            "ZIP_CODE": f"02{random.randint(100, 299)}",
            "BLOOD_GROUP": random.choice(["O+", "A+", "B+", "AB+", "O-", "A-"]),
            "PRIMARY_PHYSICIAN": random.choice(PHYSICIANS),
            "CHRONIC_CONDITIONS": random.choice(common_conditions),
            "ACTIVE_MEDICATIONS": random.choice(common_med_groups),
            "RISK_DECIL_SCORE": risk_score,
            "RISK_STRATIFICATION": risk_strat,
            "INSURANCE_PLAN": random.choice(["Medicare Advantage PPO", "Commercial HMO", "MassHealth Medicaid", "Standard PPO"])
        })
    
    patients_file = os.path.join(CSV_DIR, "patients.csv")
    with open(patients_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(patients[0].keys()))
        writer.writeheader()
        writer.writerows(patients)
    print(f"Generated {len(patients)} patients in {patients_file}")
    return patients

# ==============================================================================
# 2. GENERATE LOINC LAB RESULTS
# ==============================================================================

def generate_labs(patients):
    labs = []
    lab_id_counter = 10001
    
    # PT-1001 Longitudinal eGFR Drop (Hero 1 Contraindication)
    egfr_trajectory = [
        ("2025-02-10", 52.4, "mL/min/1.73m2", "> 60.0", "Mild to Moderate Reduction (Stage 3a)", "L"),
        ("2025-08-15", 41.2, "mL/min/1.73m2", "> 60.0", "Moderate to Severe Reduction (Stage 3b)", "L"),
        ("2026-02-12", 33.8, "mL/min/1.73m2", "> 60.0", "Approaching Severe Reduction", "L"),
        ("2026-08-20", 28.1, "mL/min/1.73m2", "> 60.0", "Severe Reduction (Stage 4) - CRITICAL CONTRAINDICATION", "LL")
    ]
    for date_str, val, units, ref, interp, flag in egfr_trajectory:
        labs.append({
            "LAB_ID": f"LAB-{lab_id_counter}",
            "PATIENT_ID": "PT-1001",
            "COLLECTION_DATE": date_str,
            "LOINC_CODE": "33914-3",
            "TEST_NAME": "Glomerular Filtration Rate (eGFR/1.73m2)",
            "NUMERIC_VALUE": val,
            "UNITS": units,
            "REFERENCE_RANGE": ref,
            "INTERPRETATION": interp,
            "ABNORMAL_FLAG": flag,
            "ORDERING_PHYSICIAN": "Dr. Robert Harrison, MD"
        })
        lab_id_counter += 1

    # PT-1001 Serum Creatinine Spike
    creat_trajectory = [
        ("2025-02-10", 1.35, "mg/dL", "0.50 - 1.10", "Mild Elevation", "H"),
        ("2025-08-15", 1.62, "mg/dL", "0.50 - 1.10", "Elevated", "H"),
        ("2026-02-12", 1.95, "mg/dL", "0.50 - 1.10", "Elevated", "H"),
        ("2026-08-20", 2.45, "mg/dL", "0.50 - 1.10", "Critical Renal Impairment", "HH")
    ]
    for date_str, val, units, ref, interp, flag in creat_trajectory:
        labs.append({
            "LAB_ID": f"LAB-{lab_id_counter}",
            "PATIENT_ID": "PT-1001",
            "COLLECTION_DATE": date_str,
            "LOINC_CODE": "2160-0",
            "TEST_NAME": "Creatinine, Serum",
            "NUMERIC_VALUE": val,
            "UNITS": units,
            "REFERENCE_RANGE": ref,
            "INTERPRETATION": interp,
            "ABNORMAL_FLAG": flag,
            "ORDERING_PHYSICIAN": "Dr. Robert Harrison, MD"
        })
        lab_id_counter += 1

    # PT-1002 Overdue HbA1c (Hero 2 Care Gap)
    labs.append({
        "LAB_ID": f"LAB-{lab_id_counter}",
        "PATIENT_ID": "PT-1002",
        "COLLECTION_DATE": "2025-05-10", # 15 months ago!
        "LOINC_CODE": "4548-4",
        "TEST_NAME": "Hemoglobin A1c (HbA1c)",
        "NUMERIC_VALUE": 8.7,
        "UNITS": "%",
        "REFERENCE_RANGE": "< 5.7",
        "INTERPRETATION": "Poor Glycemic Control (HEDIS Gap Flag)",
        "ABNORMAL_FLAG": "H",
        "ORDERING_PHYSICIAN": "Dr. Sarah Jenkins, MD"
    })
    lab_id_counter += 1

    # PT-1003 Occult Anemia & Cardiac Stress (Hero 3 Polypharmacy / Bleeding)
    labs.append({
        "LAB_ID": f"LAB-{lab_id_counter}",
        "PATIENT_ID": "PT-1003",
        "COLLECTION_DATE": "2026-08-14",
        "LOINC_CODE": "718-7",
        "TEST_NAME": "Hemoglobin, Blood",
        "NUMERIC_VALUE": 9.4,
        "UNITS": "g/dL",
        "REFERENCE_RANGE": "13.8 - 17.2",
        "INTERPRETATION": "Moderate Anemia (Potential Occult GI Bleeding)",
        "ABNORMAL_FLAG": "L",
        "ORDERING_PHYSICIAN": "Dr. David Kim, MD"
    })
    lab_id_counter += 1
    
    labs.append({
        "LAB_ID": f"LAB-{lab_id_counter}",
        "PATIENT_ID": "PT-1003",
        "COLLECTION_DATE": "2026-08-14",
        "LOINC_CODE": "42637-9",
        "TEST_NAME": "B-Type Natriuretic Peptide (BNP)",
        "NUMERIC_VALUE": 780.0,
        "UNITS": "pg/mL",
        "REFERENCE_RANGE": "< 100.0",
        "INTERPRETATION": "Decompensated Heart Failure Exacerbation",
        "ABNORMAL_FLAG": "HH",
        "ORDERING_PHYSICIAN": "Dr. David Kim, MD"
    })
    lab_id_counter += 1

    # Standard Labs for all patients
    standard_tests = [
        ("4548-4", "Hemoglobin A1c (HbA1c)", 5.2, 7.8, "%", "< 5.7"),
        ("2160-0", "Creatinine, Serum", 0.7, 1.4, "mg/dL", "0.50 - 1.10"),
        ("33914-3", "Glomerular Filtration Rate (eGFR)", 55.0, 95.0, "mL/min/1.73m2", "> 60.0"),
        ("2093-3", "Cholesterol, Total", 160.0, 240.0, "mg/dL", "< 200.0"),
        ("2085-9", "HDL Cholesterol", 40.0, 65.0, "mg/dL", "> 40.0"),
        ("13457-7", "LDL Cholesterol", 80.0, 160.0, "mg/dL", "< 100.0"),
        ("718-7", "Hemoglobin, Blood", 12.0, 16.5, "g/dL", "12.0 - 16.0")
    ]

    for p in patients:
        pid = p["PATIENT_ID"]
        # Generate 4-8 labs for each patient
        for _ in range(random.randint(4, 8)):
            code, name, min_v, max_v, units, ref = random.choice(standard_tests)
            val = round(random.uniform(min_v, max_v), 1)
            flag = "N"
            interp = "Within Normal Limits"
            if "eGFR" in name and val < 60:
                flag = "L"
                interp = "Mild Renal Reduction"
            elif "HbA1c" in name and val > 6.5:
                flag = "H"
                interp = "Diabetic Range"
            elif "Cholesterol" in name and val > 200:
                flag = "H"
                interp = "Borderline High"
                
            labs.append({
                "LAB_ID": f"LAB-{lab_id_counter}",
                "PATIENT_ID": pid,
                "COLLECTION_DATE": (datetime.now() - timedelta(days=random.randint(10, 365))).strftime("%Y-%m-%d"),
                "LOINC_CODE": code,
                "TEST_NAME": name,
                "NUMERIC_VALUE": val,
                "UNITS": units,
                "REFERENCE_RANGE": ref,
                "INTERPRETATION": interp,
                "ABNORMAL_FLAG": flag,
                "ORDERING_PHYSICIAN": p["PRIMARY_PHYSICIAN"]
            })
            lab_id_counter += 1

    labs_file = os.path.join(CSV_DIR, "lab_results.csv")
    with open(labs_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(labs[0].keys()))
        writer.writeheader()
        writer.writerows(labs)
    print(f"Generated {len(labs)} lab records in {labs_file}")
    return labs

# ==============================================================================
# 3. GENERATE ENCOUNTERS & CLAIMS
# ==============================================================================

def generate_encounters_and_claims(patients):
    encounters = []
    claims = []
    enc_counter = 5001
    claim_counter = 8001
    
    # PT-1001 Hero Encounters
    encounters.append({
        "ENCOUNTER_ID": f"ENC-{enc_counter}",
        "PATIENT_ID": "PT-1001",
        "ENCOUNTER_DATE": "2026-08-20",
        "ENCOUNTER_TYPE": "Outpatient Follow-up",
        "CHIEF_COMPLAINT": "Fatigue, mild nausea, persistent peripheral edema",
        "PROVIDER_NAME": "Dr. Robert Harrison, MD",
        "FACILITY_NAME": "Commonwealth Internal Medicine Associates",
        "DIAGNOSIS_CODES": "E11.9, I10, N18.4",
        "DISCHARGE_SUMMARY": "Patient Eleanor Vance seen for 6-month diabetic evaluation. Noted ongoing fatigue and mild anorexia. Recent lab work confirms progressive decline in renal function with eGFR dropping to 28 mL/min/1.73m2. Currently taking Metformin 1000mg BID. Urgent pharmacovigilance review required."
    })
    claims.append({
        "CLAIM_ID": f"CLM-{claim_counter}",
        "PATIENT_ID": "PT-1001",
        "SERVICE_DATE": "2026-08-20",
        "CPT_CODE": "99214",
        "SERVICE_DESCRIPTION": "Office Outpatient Visit, Level 4 (Complex Medical Decision Making)",
        "TOTAL_CHARGES": 285.00,
        "PAID_AMOUNT": 210.50,
        "CLAIM_STATUS": "Paid"
    })
    enc_counter += 1
    claim_counter += 1

    # PT-1003 Hero Catastrophic Encounters & Claims (Over $64k total spend)
    pt1003_spend_events = [
        ("2026-01-15", "Inpatient Hospitalization", "Congestive heart failure exacerbation with orthopnea", "99223", "Hospital Inpatient Care, High Severity", 24500.00, 21800.00),
        ("2026-04-10", "Emergency Department", "Dizziness, acute melena, severe hip pain flare", "99285", "Emergency Dept Visit, Immediate Threat", 8900.00, 7400.00),
        ("2026-07-22", "Inpatient Observation", "Syncope investigation; telemetry monitoring; acute-on-chronic renal injury", "99219", "Initial Observation Care", 18200.00, 16100.00),
        ("2026-08-14", "Cardiology Specialty Visit", "Atrial fibrillation evaluation with severe polypharmacy review", "99244", "Specialist Consultation", 12650.00, 10200.00)
    ]
    for edate, etype, complaint, cpt, cdesc, charges, paid in pt1003_spend_events:
        encounters.append({
            "ENCOUNTER_ID": f"ENC-{enc_counter}",
            "PATIENT_ID": "PT-1003",
            "ENCOUNTER_DATE": edate,
            "ENCOUNTER_TYPE": etype,
            "CHIEF_COMPLAINT": complaint,
            "PROVIDER_NAME": "Dr. David Kim, MD",
            "FACILITY_NAME": "Massachusetts General Healthcare Pavilion",
            "DIAGNOSIS_CODES": "I48.91, I50.9, M19.90, K21.9",
            "DISCHARGE_SUMMARY": f"Patient Arthur Pendelton treated for {complaint}. Longitudinal medication burden exceeds 9 active concurrent prescriptions including Eliquis (Apixaban 5mg) and concurrent high-dose NSAID (Ibuprofen 800mg TID). High-risk catastrophic spend category."
        })
        claims.append({
            "CLAIM_ID": f"CLM-{claim_counter}",
            "PATIENT_ID": "PT-1003",
            "SERVICE_DATE": edate,
            "CPT_CODE": cpt,
            "SERVICE_DESCRIPTION": cdesc,
            "TOTAL_CHARGES": charges,
            "PAID_AMOUNT": paid,
            "CLAIM_STATUS": "Paid"
        })
        enc_counter += 1
        claim_counter += 1

    # Standard Encounters & Claims for remaining patients
    for p in patients:
        pid = p["PATIENT_ID"]
        for _ in range(random.randint(2, 5)):
            enc_date = (datetime.now() - timedelta(days=random.randint(20, 365))).strftime("%Y-%m-%d")
            encounters.append({
                "ENCOUNTER_ID": f"ENC-{enc_counter}",
                "PATIENT_ID": pid,
                "ENCOUNTER_DATE": enc_date,
                "ENCOUNTER_TYPE": random.choice(["Routine Preventive", "Outpatient Follow-up", "Telehealth Video Consult"]),
                "CHIEF_COMPLAINT": "Routine chronic condition management and medication reconciliation",
                "PROVIDER_NAME": p["PRIMARY_PHYSICIAN"],
                "FACILITY_NAME": "Metro Boston Ambulatory Care Network",
                "DIAGNOSIS_CODES": "Z00.00, I10, E78.5",
                "DISCHARGE_SUMMARY": "Patient reviewed. Vitals stable. Encouraged lifestyle adherence, physical activity, and continued compliance with active pharmacy orders."
            })
            charges = round(random.uniform(120.0, 450.0), 2)
            claims.append({
                "CLAIM_ID": f"CLM-{claim_counter}",
                "PATIENT_ID": pid,
                "SERVICE_DATE": enc_date,
                "CPT_CODE": random.choice(["99213", "99214", "99396", "99442"]),
                "SERVICE_DESCRIPTION": "Outpatient Office Visit / Preventative Screening",
                "TOTAL_CHARGES": charges,
                "PAID_AMOUNT": round(charges * 0.78, 2),
                "CLAIM_STATUS": "Paid"
            })
            enc_counter += 1
            claim_counter += 1

    enc_file = os.path.join(CSV_DIR, "encounters.csv")
    with open(enc_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(encounters[0].keys()))
        writer.writeheader()
        writer.writerows(encounters)
    print(f"Generated {len(encounters)} encounters in {enc_file}")

    claims_file = os.path.join(CSV_DIR, "claims.csv")
    with open(claims_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(claims[0].keys()))
        writer.writeheader()
        writer.writerows(claims)
    print(f"Generated {len(claims)} claims in {claims_file}")

# ==============================================================================
# 4. GENERATE UNSTRUCTURED CLINICAL REFERENCE DOCUMENTS (FDA & NOTES)
# ==============================================================================

def generate_clinical_docs():
    # 1. FDA Metformin Package Insert
    fda_metformin = """UNITED STATES FOOD AND DRUG ADMINISTRATION (FDA)
HIGHLIGHTS OF PRESCRIBING INFORMATION: GLUCOPHAGE (METFORMIN HYDROCHLORIDE) TABLETS
Initial U.S. Approval: 1995 | Revised: 01/2026

WARNING: LACTIC ACIDOSIS
Postmarketing cases of metformin-associated lactic acidosis have resulted in death, hypothermia, hypotension, and resistant bradyarrhythmias. The onset is often subtle, accompanied only by nonspecific symptoms such as malaise, myalgias, respiratory distress, somnolence, and abdominal pain.

4. CONTRAINDICATIONS
GLUCOPHAGE is contraindicated in patients with:
- Severe renal impairment (eGFR below 30 mL/min/1.73 m2).
- Known hypersensitivity to metformin hydrochloride.
- Acute or chronic metabolic acidosis, including diabetic ketoacidosis, with or without coma.

5. WARNINGS AND PRECAUTIONS
5.1 Lactic Acidosis
The risk of metformin-associated lactic acidosis increases with the degree of renal impairment because metformin is substantially excreted by the kidney. 
Before initiating GLUCOPHAGE, obtain an estimated glomerular filtration rate (eGFR).
- In patients with an eGFR below 30 mL/min/1.73 m2, initiation of GLUCOPHAGE is contraindicated.
- In patients currently taking GLUCOPHAGE whose eGFR subsequently falls below 30 mL/min/1.73 m2, discontinue GLUCOPHAGE immediately.
- In patients with an eGFR between 30 and 45 mL/min/1.73 m2, assessing the benefits and risks of continuing therapy is recommended; if prescribed, limit total daily dosage to 1000 mg and monitor renal function at least every 3 months.
"""
    with open(os.path.join(DOCS_DIR, "FDA_Metformin_Package_Insert.txt"), "w", encoding="utf-8") as f:
        f.write(fda_metformin)

    # 2. FDA Eliquis (Apixaban) Package Insert
    fda_eliquis = """UNITED STATES FOOD AND DRUG ADMINISTRATION (FDA)
PRESCRIBING INFORMATION: ELIQUIS (APIXABAN) TABLETS, FOR ORAL USE
Revised: 02/2026

WARNING: (A) PREMATURE DISCONTINUATION INCREASES RISK OF THROMBOTIC EVENTS; (B) SPINAL/EPIDURAL HEMATOMA

4. CONTRAINDICATIONS
- Active pathological bleeding.
- Severe hypersensitivity to apixaban.

7. DRUG INTERACTIONS
7.1 Concomitant Use with Anticoagulants and Antiplatelet Agents
Co-administration of antiplatelet agents, fibrinolytics, heparin, aspirin, and chronic NSAID therapy increases the risk of bleeding.
Nonsteroidal Anti-Inflammatory Drugs (NSAIDs):
Concomitant administration of ELIQUIS with NSAIDs (such as ibuprofen, naproxen, or indomethacin) elevates platelet dysfunction and gastrointestinal mucosal irritation, resulting in a statistically significant increase in major gastrointestinal hemorrhage and intracranial bleed risk.
Recommendation: Avoid concurrent administration of chronic high-dose NSAIDs with ELIQUIS unless clinically mandated and accompanied by gastroprotective agents (e.g., Proton Pump Inhibitors).
"""
    with open(os.path.join(DOCS_DIR, "FDA_Eliquis_Package_Insert.txt"), "w", encoding="utf-8") as f:
        f.write(fda_eliquis)

    # 3. HEDIS MY2026 Quality Measurement Specification
    hedis_diabetes = """NATIONAL COMMITTEE FOR QUALITY ASSURANCE (NCQA)
HEALTHCARE EFFECTIVENESS DATA AND INFORMATION SET (HEDIS MY2026)
MEASURE SPECIFICATION: Comprehensive Diabetes Care (CDC) / NQF-0059

1. MEASURE DESCRIPTION
The percentage of members 18–75 years of age with diabetes (type 1 and type 2) who had each of the following during the measurement year:
- Hemoglobin A1c (HbA1c) testing completed at least once every 12 months.
- HbA1c Poor Control (>9.0%).
- HbA1c Control (<8.0%).
- Retinal eye exam performed by an eye care professional.
- Blood pressure control (<140/90 mm Hg).

2. CLINICAL RATIONALE & CMS STAR RATING IMPACT
Diabetic patients without an annual HbA1c observation directly penalize Medicare Advantage Star Ratings (Triple-Weighted Clinical Measure). Health plans failing to achieve the 75th percentile threshold incur substantial financial penalties under the CMS Quality Bonus Payment (QBP) framework.

3. OUTREACH BENCHMARK
Any attributed member exceeding 12 months since the last verified LOINC 4548-4 lab observation must be routed to prioritized clinical navigation for point-of-care lab order dispatch.
"""
    with open(os.path.join(DOCS_DIR, "HEDIS_MY2026_Diabetes_Guidelines.txt"), "w", encoding="utf-8") as f:
        f.write(hedis_diabetes)

    # 4. Hero 1 Note (Eleanor Vance)
    note_pt1001 = """CLINICAL ENCOUNTER PROGRESS NOTE
PATIENT NAME: Vance, Eleanor | MRN: PT-1001 | DOB: 1958-04-12 (68F)
DATE OF SERVICE: 2026-08-20 | PROVIDER: Dr. Robert Harrison, MD
CLINICAL SPECIALTY: Internal Medicine / Geriatric Care

SUBJECTIVE:
Patient presents accompanied by daughter for scheduled chronic disease follow-up. Reports generalized fatigue, progressive lethargy over the past 3 weeks, and mild morning nausea. Denies acute fever, chills, chest pressure, or shortness of breath.

CURRENT MEDICATIONS (Confirmed by Reconciliation):
1. Metformin HCl 1000 mg oral tablet - 1 tablet twice daily with meals.
2. Lisinopril 20 mg oral tablet - 1 tablet daily in the morning.
3. Atorvastatin calcium 40 mg oral tablet - 1 tablet at bedtime.

LABORATORY TELEMETRY REVIEW:
Reviewed blood work drawn on 2026-08-20:
- Serum Creatinine: 2.45 mg/dL (Baseline was 1.35 mg/dL in Feb 2025).
- Estimated GFR: 28.1 mL/min/1.73m2 (Decline from 52.4 mL/min over 18 months).
- Serum Potassium: 5.1 mEq/L (Borderline high).

ASSESSMENT & CLINICAL PLAN:
1. Acute-on-Chronic Kidney Disease (Stage 4, severe impairment).
2. Type 2 Diabetes Mellitus with worsening renal excretion.
CRITICAL SAFETY CONCERN: Given eGFR has plummeted below 30 mL/min/1.73m2, continued use of Metformin carries acute boxed warning for fatal Lactic Acidosis. Immediate medication cessation indicated. Plan to discontinue Metformin and transition to DPP-4 or renal-adjusted insulin. Alert sent to outpatient pharmacy.
"""
    with open(os.path.join(DOCS_DIR, "Clinical_Encounter_Note_PT1001.txt"), "w", encoding="utf-8") as f:
        f.write(note_pt1001)

    # 5. Hero 2 Note (Marcus Brody)
    note_pt1002 = """PRIMARY CARE ANNUAL WELLNESS VISIT
PATIENT NAME: Brody, Marcus | MRN: PT-1002 | DOB: 1972-09-24 (54M)
DATE OF SERVICE: 2026-07-15 | PROVIDER: Dr. Sarah Jenkins, MD

HISTORY OF PRESENT ILLNESS:
Patient Marcus Brody presents for annual preventative exam. Reports feeling reasonably well. Exercises inconsistently. Admits dietary indiscretions with carbohydrates.

CHRONIC CONDITION & CARE GAP AUDIT:
1. Type 2 Diabetes Mellitus:
   - Chart audit reveals LAST verified HbA1c test was performed on 2025-05-10 (Value: 8.7%).
   - Over 14 months elapsed without repeat glycemic evaluation.
   - Patient is currently non-compliant with NCQA HEDIS NQF-0059 annual testing standard.
2. Preventative Gaps:
   - Overdue for diabetic foot monofilament exam.
   - Dilated retinal exam overdue by 6 months.

PLAN:
- Schedule immediate in-clinic fingerstick HbA1c or venous blood draw.
- Dispatch care coordinator task for diabetic education and home test kit shipment.
"""
    with open(os.path.join(DOCS_DIR, "Annual_Wellness_Visit_PT1002.txt"), "w", encoding="utf-8") as f:
        f.write(note_pt1002)

    # 6. Hero 3 Note (Arthur Pendelton)
    note_pt1003 = """INPATIENT DISCHARGE SUMMARY & POLYPHARMACY RECONCILIATION
PATIENT NAME: Pendelton, Arthur | MRN: PT-1003 | DOB: 1952-11-03 (74M)
ADMISSION DATE: 2026-08-10 | DISCHARGE DATE: 2026-08-14
FACILITY: Massachusetts General Hospital | ATTENDING: Dr. David Kim, MD (Cardiology)

DISCHARGE DIAGNOSES:
1. Non-valvular Atrial Fibrillation (CHA2DS2-VASc score = 4).
2. Congestive Heart Failure with preserved ejection fraction (HFpEF, NYHA Class III).
3. Severe bilateral knee osteoarthritis with chronic joint pain.
4. Mild normocytic anemia secondary to suspected subclinical upper GI blood loss.

HOSPITAL COURSE & PHARMACY TOXICOLOGY AUDIT:
Patient admitted following near-syncope and episode of dark, tarry stools at home. Comprehensive pharmacy reconciliation revealed patient has been concurrently consuming Apixaban (Eliquis) 5mg BID for stroke prophylaxis alongside over-the-counter and prescribed Ibuprofen 800mg TID for chronic severe knee pain.
Total active medication count is 9 distinct pharmaceuticals. Cumulative claims expenditure over the trailing 12 months stands at $64,250, placing patient in the top 1% catastrophic risk decile.

RECOMMENDATIONS AT DISCHARGE:
1. Immediate and strict cessation of all oral NSAIDs (Ibuprofen).
2. Transition analgesia to topical lidocaine patches and monitored acetaminophen.
3. Outpatient gastroenterology endoscopy referral within 14 days.
4. Care management enrollment under GCC High-Risk Care Coordination Program.
"""
    with open(os.path.join(DOCS_DIR, "Discharge_Summary_PT1003.txt"), "w", encoding="utf-8") as f:
        f.write(note_pt1003)

    print(f"Generated 6 core clinical and regulatory documents in {DOCS_DIR}")

# ==============================================================================
# MAIN EXECUTION
# ==============================================================================

if __name__ == "__main__":
    print("Starting AegisCortex AI Synthetic Clinical Data Generation...")
    pts = generate_patients()
    labs = generate_labs(pts)
    generate_encounters_and_claims(pts)
    generate_clinical_docs()
    print("SUCCESS: All clinical datasets and reference documents successfully generated.")
