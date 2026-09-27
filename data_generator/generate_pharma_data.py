"""
AegisCortex AI - Enterprise Pharma Synthetic Data Generator
Generates realistic Master Data Management (MDM), Territory Alignment,
Market Access & Prior Authorization (PA), and Longitudinal Prescription Events.
"""

import os
import random
from pathlib import Path
import pandas as pd
import numpy as np

# Seed for reproducibility
random.seed(42)
np.random.seed(42)

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_CSV_DIR = BASE_DIR / "data" / "raw_csv"
RAW_CSV_DIR.mkdir(parents=True, exist_ok=True)

def generate_mdm_hco():
    hcos = [
        {"HCO_ID": "HCO-001", "HCO_NAME": "Penn Medicine Health System", "HCO_TYPE": "Academic Integrated Delivery Network (IDN)", "TIN": "23-1489210", "PARENT_IDN_NAME": "University of Pennsylvania Health System", "CITY": "Philadelphia", "STATE": "PA", "ZIP5": "19104", "BEDS_COUNT": 1640, "PT_COMMITTEE_STATUS": "Preferred (Tier 2 Biologics)", "PROTOCOL_RESTRICTION_LEVEL": "Low"},
        {"HCO_ID": "HCO-002", "HCO_NAME": "Thomas Jefferson University Hospitals", "HCO_TYPE": "Integrated Delivery Network (IDN)", "TIN": "23-2948172", "PARENT_IDN_NAME": "Jefferson Health", "CITY": "Philadelphia", "STATE": "PA", "ZIP5": "19107", "BEDS_COUNT": 980, "PT_COMMITTEE_STATUS": "Step-Therapy Required (TNF Failure)", "PROTOCOL_RESTRICTION_LEVEL": "Moderate"},
        {"HCO_ID": "HCO-003", "HCO_NAME": "Temple Health Episcopal Campus", "HCO_TYPE": "Safety Net / 340B Hospital", "TIN": "23-3019284", "PARENT_IDN_NAME": "Temple University Health System", "CITY": "Philadelphia", "STATE": "PA", "ZIP5": "19140", "BEDS_COUNT": 720, "PT_COMMITTEE_STATUS": "Restricted (Prior Auth Enforced)", "PROTOCOL_RESTRICTION_LEVEL": "High"},
        {"HCO_ID": "HCO-004", "HCO_NAME": "UPMC Presbyterian Shadyside", "HCO_TYPE": "Academic Medical Center", "TIN": "25-0192847", "PARENT_IDN_NAME": "UPMC Health Network", "CITY": "Pittsburgh", "STATE": "PA", "ZIP5": "15213", "BEDS_COUNT": 1200, "PT_COMMITTEE_STATUS": "Preferred (Tier 2 Biologics)", "PROTOCOL_RESTRICTION_LEVEL": "Low"},
        {"HCO_ID": "HCO-005", "HCO_NAME": "Geisinger Medical Center", "HCO_TYPE": "Integrated Closed Payer-Provider Network", "TIN": "24-9182736", "PARENT_IDN_NAME": "Geisinger Health", "CITY": "Danville", "STATE": "PA", "ZIP5": "17822", "BEDS_COUNT": 540, "PT_COMMITTEE_STATUS": "Clinical Pathway Concordant", "PROTOCOL_RESTRICTION_LEVEL": "Moderate"},
        {"HCO_ID": "HCO-006", "HCO_NAME": "Main Line Health (Lankenau Medical Center)", "HCO_TYPE": "Community Health System", "TIN": "23-5592819", "PARENT_IDN_NAME": "Main Line Health", "CITY": "Wynnewood", "STATE": "PA", "ZIP5": "19096", "BEDS_COUNT": 490, "PT_COMMITTEE_STATUS": "Preferred (Tier 2 Biologics)", "PROTOCOL_RESTRICTION_LEVEL": "Low"},
    ]
    df = pd.DataFrame(hcos)
    df.to_csv(RAW_CSV_DIR / "mdm_hco_master.csv", index=False)
    print(f"[*] Generated {len(df)} HCO MDM records.")
    return df

def generate_dim_territory():
    territories = [
        {"TERRITORY_ID": "US-PA-PHILLY-01", "REGION_ID": "REG-NORTHEAST", "AREA_ID": "AREA-MIDATLANTIC", "TERRITORY_NAME": "Philadelphia Center City & Main Line", "ASSIGNED_REP_NAME": "Marcus Vance", "TARGET_CALL_CAPACITY": 240, "QUOTA_TRX": 4500},
        {"TERRITORY_ID": "US-PA-PHILLY-02", "REGION_ID": "REG-NORTHEAST", "AREA_ID": "AREA-MIDATLANTIC", "TERRITORY_NAME": "Philadelphia North & Bucks County", "ASSIGNED_REP_NAME": "Jessica Miller", "TARGET_CALL_CAPACITY": 220, "QUOTA_TRX": 3800},
        {"TERRITORY_ID": "US-NE-T12", "REGION_ID": "REG-NORTHEAST", "AREA_ID": "AREA-KEYSTONE", "TERRITORY_NAME": "Greater Pennsylvania & Delaware Valley", "ASSIGNED_REP_NAME": "David Ross", "TARGET_CALL_CAPACITY": 260, "QUOTA_TRX": 5200},
        {"TERRITORY_ID": "US-NY-METRO-01", "REGION_ID": "REG-NORTHEAST", "AREA_ID": "AREA-TRISTATE", "TERRITORY_NAME": "New York Metro South & Manhattan", "ASSIGNED_REP_NAME": "Elena Rostova", "TARGET_CALL_CAPACITY": 280, "QUOTA_TRX": 6100}
    ]
    df = pd.DataFrame(territories)
    df.to_csv(RAW_CSV_DIR / "dim_territory.csv", index=False)
    print(f"[*] Generated {len(df)} Territory records.")
    return df

def generate_mdm_hcp():
    hcps = [
        {"HCP_ID": "HCP-001", "NPI": "1982736450", "FIRST_NAME": "Sarah", "LAST_NAME": "Jenkins", "PRIMARY_SPECIALTY": "Dermatology", "TAXONOMY_CODE": "207N00000X", "PRACTICE_ADDRESS": "3400 Civic Center Blvd", "CITY": "Philadelphia", "STATE": "PA", "ZIP5": "19104", "DEA_NUMBER": "BJ1982736", "AMA_ID": "01827491", "IDN_AFFILIATION_ID": "HCO-001", "PRESCRIBER_DECILE": 10, "PEER_RANKING": "Top 1% Regional KOL"},
        {"HCP_ID": "HCP-002", "NPI": "1205948372", "FIRST_NAME": "Robert", "LAST_NAME": "Chen", "PRIMARY_SPECIALTY": "Dermatology", "TAXONOMY_CODE": "207N00000X", "PRACTICE_ADDRESS": "833 Chestnut St, Ste 740", "CITY": "Philadelphia", "STATE": "PA", "ZIP5": "19107", "DEA_NUMBER": "BC1205948", "AMA_ID": "02938471", "IDN_AFFILIATION_ID": "HCO-002", "PRESCRIBER_DECILE": 9, "PEER_RANKING": "Top 5% High Prescriber"},
        {"HCP_ID": "HCP-003", "NPI": "1493028174", "FIRST_NAME": "Anthony", "LAST_NAME": "Russo", "PRIMARY_SPECIALTY": "Nephrology", "TAXONOMY_CODE": "207RN0300X", "PRACTICE_ADDRESS": "3401 N Broad St", "CITY": "Philadelphia", "STATE": "PA", "ZIP5": "19140", "DEA_NUMBER": "BR1493028", "AMA_ID": "03847192", "IDN_AFFILIATION_ID": "HCO-003", "PRESCRIBER_DECILE": 8, "PEER_RANKING": "Renal Care Guideline Leader"},
        {"HCP_ID": "HCP-004", "NPI": "1789420193", "FIRST_NAME": "Emily", "LAST_NAME": "Watson", "PRIMARY_SPECIALTY": "Endocrinology", "TAXONOMY_CODE": "207RE0101X", "PRACTICE_ADDRESS": "3701 Market St, Ste 400", "CITY": "Philadelphia", "STATE": "PA", "ZIP5": "19104", "DEA_NUMBER": "BW1789420", "AMA_ID": "04829104", "IDN_AFFILIATION_ID": "HCO-001", "PRESCRIBER_DECILE": 10, "PEER_RANKING": "ADA Regional Committee Chair"},
        {"HCP_ID": "HCP-005", "NPI": "1639201948", "FIRST_NAME": "Michael", "LAST_NAME": "Patel", "PRIMARY_SPECIALTY": "Cardiology", "TAXONOMY_CODE": "207RC0000X", "PRACTICE_ADDRESS": "100 E Lancaster Ave", "CITY": "Wynnewood", "STATE": "PA", "ZIP5": "19096", "DEA_NUMBER": "BP1639201", "AMA_ID": "05918273", "IDN_AFFILIATION_ID": "HCO-006", "PRESCRIBER_DECILE": 9, "PEER_RANKING": "Top 5% Interventional Cardiology"},
        {"HCP_ID": "HCP-006", "NPI": "1582910394", "FIRST_NAME": "Lisa", "LAST_NAME": "Nguyen", "PRIMARY_SPECIALTY": "Rheumatology", "TAXONOMY_CODE": "207RR0500X", "PRACTICE_ADDRESS": "925 Chestnut St", "CITY": "Philadelphia", "STATE": "PA", "ZIP5": "19107", "DEA_NUMBER": "BN1582910", "AMA_ID": "06918274", "IDN_AFFILIATION_ID": "HCO-002", "PRESCRIBER_DECILE": 9, "PEER_RANKING": "Top 5% Biologics Prescriber"},
        {"HCP_ID": "HCP-007", "NPI": "1394019284", "FIRST_NAME": "David", "LAST_NAME": "Goldman", "PRIMARY_SPECIALTY": "Dermatology", "TAXONOMY_CODE": "207N00000X", "PRACTICE_ADDRESS": "200 Lothrop St", "CITY": "Pittsburgh", "STATE": "PA", "ZIP5": "15213", "DEA_NUMBER": "BG1394019", "AMA_ID": "07819203", "IDN_AFFILIATION_ID": "HCO-004", "PRESCRIBER_DECILE": 8, "PEER_RANKING": "Key Account Specialist"},
        {"HCP_ID": "HCP-008", "NPI": "1849201837", "FIRST_NAME": "Rachel", "LAST_NAME": "Kaufman", "PRIMARY_SPECIALTY": "Dermatology", "TAXONOMY_CODE": "207N00000X", "PRACTICE_ADDRESS": "100 N Academy Ave", "CITY": "Danville", "STATE": "PA", "ZIP5": "17822", "DEA_NUMBER": "BK1849201", "AMA_ID": "08918293", "IDN_AFFILIATION_ID": "HCO-005", "PRESCRIBER_DECILE": 7, "PEER_RANKING": "Rural Payer-Provider Lead"},
        {"HCP_ID": "HCP-009", "NPI": "1192837465", "FIRST_NAME": "Brian", "LAST_NAME": "O'Connor", "PRIMARY_SPECIALTY": "Primary Care / Internal Medicine", "TAXONOMY_CODE": "207Q00000X", "PRACTICE_ADDRESS": "230 N Broad St", "CITY": "Philadelphia", "STATE": "PA", "ZIP5": "19102", "DEA_NUMBER": "BO1192837", "AMA_ID": "09817264", "IDN_AFFILIATION_ID": "HCO-003", "PRESCRIBER_DECILE": 6, "PEER_RANKING": "Community Practice Lead"},
        {"HCP_ID": "HCP-010", "NPI": "1928374650", "FIRST_NAME": "Karen", "LAST_NAME": "Washington", "PRIMARY_SPECIALTY": "Dermatology", "TAXONOMY_CODE": "207N00000X", "PRACTICE_ADDRESS": "51 N 39th St", "CITY": "Philadelphia", "STATE": "PA", "ZIP5": "19104", "DEA_NUMBER": "BW1928374", "AMA_ID": "10928374", "IDN_AFFILIATION_ID": "HCO-001", "PRESCRIBER_DECILE": 9, "PEER_RANKING": "Psoriasis Phototherapy Director"}
    ]
    df = pd.DataFrame(hcps)
    df.to_csv(RAW_CSV_DIR / "mdm_hcp_master.csv", index=False)
    print(f"[*] Generated {len(df)} HCP MDM records.")
    return df

def generate_hcp_alignment(df_hcp):
    alignments = []
    territory_map = {
        "HCP-001": ("US-PA-PHILLY-01", 96.4, 10, 24, 1.2, 21),
        "HCP-002": ("US-PA-PHILLY-01", 91.8, 9, 20, 1.4, 28),
        "HCP-003": ("US-PA-PHILLY-02", 84.5, 8, 16, 2.1, 42),
        "HCP-004": ("US-PA-PHILLY-01", 94.2, 10, 24, 1.1, 18),
        "HCP-005": ("US-PA-PHILLY-01", 88.0, 9, 18, 1.8, 32),
        "HCP-006": ("US-PA-PHILLY-01", 89.5, 9, 18, 1.5, 26),
        "HCP-007": ("US-NE-T12", 82.0, 8, 14, 3.2, 45),
        "HCP-008": ("US-NE-T12", 76.5, 7, 12, 3.8, 52),
        "HCP-009": ("US-PA-PHILLY-02", 71.0, 6, 10, 2.4, 60),
        "HCP-010": ("US-PA-PHILLY-01", 93.1, 9, 20, 1.3, 24),
    }
    for hcp_id, (t_id, aoi, decile, calls, imp, vel) in territory_map.items():
        alignments.append({
            "HCP_ID": hcp_id,
            "TERRITORY_ID": t_id,
            "ACCOUNT_OPPORTUNITY_INDEX": aoi,
            "TARGET_DECILE": decile,
            "CALL_FREQUENCY_ANNUAL": calls,
            "TRAVEL_IMPEDANCE_SCORE": imp,
            "CONVERSION_VELOCITY_DAYS": vel
        })
    df = pd.DataFrame(alignments)
    df.to_csv(RAW_CSV_DIR / "map_hcp_territory_alignment.csv", index=False)
    print(f"[*] Generated {len(df)} HCP Territory Alignment records.")
    return df

def generate_formulary_coverage():
    formularies = [
        {"PLAN_ID": "PLAN-CVS-COMM", "PAYER_NAME": "Aetna / CVS Health", "PBM_NAME": "CVS Caremark", "LOB": "Commercial", "NDC_CODE": "0074-1050-01", "DRUG_BRAND": "Skyrizi", "TIER_LEVEL": "Tier 2 (Preferred Brand)", "PA_REQUIRED_FLAG": "N", "STEP_THERAPY_REQUIRED_FLAG": "N", "QUANTITY_LIMIT_FLAG": "Y", "COPAY_AVG_USD": 35.00},
        {"PLAN_ID": "PLAN-CVS-COMM", "PAYER_NAME": "Aetna / CVS Health", "PBM_NAME": "CVS Caremark", "LOB": "Commercial", "NDC_CODE": "0074-3799-02", "DRUG_BRAND": "Humira", "TIER_LEVEL": "Tier 3 (Non-Preferred)", "PA_REQUIRED_FLAG": "Y", "STEP_THERAPY_REQUIRED_FLAG": "N", "QUANTITY_LIMIT_FLAG": "Y", "COPAY_AVG_USD": 95.00},
        {"PLAN_ID": "PLAN-ESI-COMM", "PAYER_NAME": "Cigna Healthcare", "PBM_NAME": "Express Scripts", "LOB": "Commercial", "NDC_CODE": "0074-1050-01", "DRUG_BRAND": "Skyrizi", "TIER_LEVEL": "Tier 2 (Preferred Brand)", "PA_REQUIRED_FLAG": "Y", "STEP_THERAPY_REQUIRED_FLAG": "N", "QUANTITY_LIMIT_FLAG": "Y", "COPAY_AVG_USD": 45.00},
        {"PLAN_ID": "PLAN-ESI-COMM", "PAYER_NAME": "Cigna Healthcare", "PBM_NAME": "Express Scripts", "LOB": "Commercial", "NDC_CODE": "0074-3799-02", "DRUG_BRAND": "Humira", "TIER_LEVEL": "Tier 3 (Non-Preferred)", "PA_REQUIRED_FLAG": "Y", "STEP_THERAPY_REQUIRED_FLAG": "Y", "QUANTITY_LIMIT_FLAG": "Y", "COPAY_AVG_USD": 110.00},
        {"PLAN_ID": "PLAN-OPTUM-MA", "PAYER_NAME": "UnitedHealthcare", "PBM_NAME": "OptumRx", "LOB": "Medicare Advantage", "NDC_CODE": "0074-1050-01", "DRUG_BRAND": "Skyrizi", "TIER_LEVEL": "Tier 4 (Specialty Tier)", "PA_REQUIRED_FLAG": "Y", "STEP_THERAPY_REQUIRED_FLAG": "N", "QUANTITY_LIMIT_FLAG": "Y", "COPAY_AVG_USD": 85.00},
        {"PLAN_ID": "PLAN-OPTUM-MA", "PAYER_NAME": "UnitedHealthcare", "PBM_NAME": "OptumRx", "LOB": "Medicare Advantage", "NDC_CODE": "0069-4210-66", "DRUG_BRAND": "Eliquis", "TIER_LEVEL": "Tier 2 (Preferred Brand)", "PA_REQUIRED_FLAG": "N", "STEP_THERAPY_REQUIRED_FLAG": "N", "QUANTITY_LIMIT_FLAG": "Y", "COPAY_AVG_USD": 30.00},
        {"PLAN_ID": "PLAN-BCBS-COMM", "PAYER_NAME": "Independence Blue Cross", "PBM_NAME": "Prime Therapeutics", "LOB": "Commercial", "NDC_CODE": "0074-1050-01", "DRUG_BRAND": "Skyrizi", "TIER_LEVEL": "Tier 2 (Preferred Brand)", "PA_REQUIRED_FLAG": "N", "STEP_THERAPY_REQUIRED_FLAG": "N", "QUANTITY_LIMIT_FLAG": "Y", "COPAY_AVG_USD": 40.00}
    ]
    df = pd.DataFrame(formularies)
    df.to_csv(RAW_CSV_DIR / "fact_formulary_tier_coverage.csv", index=False)
    print(f"[*] Generated {len(df)} Formulary Tier records.")
    return df

def generate_prescription_events():
    events = []
    drugs = [
        ("Skyrizi", "0074-1050-01", "2059343", "IL-23 Biologic", 150.0, "mg", 84, "L40.0"),
        ("Humira", "0074-3799-02", "329528", "TNF Inhibitor", 40.0, "mg", 14, "L40.0"),
        ("Stelara", "57894-060-02", "858080", "IL-12/23 Inhibitor", 45.0, "mg", 84, "L40.0"),
        ("Metformin HCl", "0093-1048-01", "860975", "Biguanide", 1000.0, "mg", 30, "E11.9"),
        ("Eliquis", "0069-4210-66", "1364430", "Direct Oral Anticoagulant", 5.0, "mg", 30, "I48.0"),
        ("Jardiance", "0597-0152-30", "1545653", "SGLT2 Inhibitor", 10.0, "mg", 30, "E11.9")
    ]
    
    hcp_pool = [
        ("1982736450", "US-PA-PHILLY-01", 0.45), # Dr. Sarah Jenkins (high Skyrizi)
        ("1205948372", "US-PA-PHILLY-01", 0.35), # Dr. Robert Chen
        ("1493028174", "US-PA-PHILLY-02", 0.10), # Dr. Anthony Russo
        ("1789420193", "US-PA-PHILLY-01", 0.15), # Dr. Emily Watson
        ("1639201948", "US-PA-PHILLY-01", 0.20), # Dr. Michael Patel
        ("1928374650", "US-PA-PHILLY-01", 0.30), # Dr. Karen Washington
        ("1394019284", "US-NE-T12", 0.25),        # Dr. David Goldman
        ("1849201837", "US-NE-T12", 0.15),        # Dr. Rachel Kaufman
    ]
    
    payers = ["PLAN-CVS-COMM", "PLAN-ESI-COMM", "PLAN-OPTUM-MA", "PLAN-BCBS-COMM"]
    statuses = ["PAID", "PAID", "PAID", "PAID", "REJECTED_PA", "REJECTED_COPAY"]
    
    for i in range(1, 281):
        evt_id = f"RX-EVT-{i:05d}"
        pt_token = f"PAT-TOK-{random.randint(1001, 1080):04d}"
        hcp_npi, territory, p_skyrizi = random.choice(hcp_pool)
        
        # Determine drug based on specialty and probability
        if random.random() < p_skyrizi:
            drug = drugs[0] # Skyrizi
        else:
            drug = random.choice(drugs)
            
        d_name, d_ndc, d_cui, d_class, d_dose, d_unit, d_freq, d_icd = drug
        
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        auth_date = f"2024-{month:02d}-{day:02d}"
        
        status = random.choice(statuses)
        copay = 35.0 if status == "PAID" else (85.0 if status == "REJECTED_COPAY" else 0.0)
        
        events.append({
            "PRESCRIPTION_EVENT_ID": evt_id,
            "PATIENT_TOKEN": pt_token,
            "PRESCRIBING_NPI": hcp_npi,
            "ENCOUNTER_ID": f"ENC-{random.randint(100, 999)}",
            "AUTHORED_DATE": auth_date,
            "ICD10_PRIMARY_DIAGNOSIS": d_icd,
            "RXNORM_CUI": d_cui,
            "NDC_CODE": d_ndc,
            "DRUG_BRAND": d_name,
            "DRUG_CLASS": d_class,
            "DOSAGE_MAGNITUDE": d_dose,
            "DOSAGE_UNIT": d_unit,
            "FREQUENCY_DAYS": d_freq,
            "REFILLS_AUTHORIZED": random.randint(1, 5),
            "PAYER_ID": random.choice(payers),
            "CLAIM_STATUS": status,
            "COPAY_COINSURANCE_USD": copay,
            "TERRITORY_ID": territory
        })
        
    df = pd.DataFrame(events)
    df.to_csv(RAW_CSV_DIR / "fact_prescription_events.csv", index=False)
    print(f"[*] Generated {len(df)} Prescription Event records.")
    return df

def generate_pa_denials():
    denials = [
        {"DENIAL_ID": "PA-DEN-001", "CLAIM_ID": "CLM-PA-9182", "PATIENT_TOKEN": "PAT-TOK-1014", "PRESCRIBING_NPI": "1982736450", "NDC_CODE": "0074-1050-01", "DRUG_BRAND": "Skyrizi", "DENIAL_DATE": "2024-11-04", "REJECTION_CODE": "X12-75", "REJECTION_REASON": "Prior Authorization Required / Missing Step Therapy Attestation", "RECOVERABLE_REVENUE_USD": 14200.00, "APPEAL_STATUS": "OVERTURNED", "TERRITORY_ID": "US-PA-PHILLY-01"},
        {"DENIAL_ID": "PA-DEN-002", "CLAIM_ID": "CLM-PA-9183", "PATIENT_TOKEN": "PAT-TOK-1022", "PRESCRIBING_NPI": "1982736450", "NDC_CODE": "0074-1050-01", "DRUG_BRAND": "Skyrizi", "DENIAL_DATE": "2024-11-08", "REJECTION_CODE": "X12-197", "REJECTION_REASON": "Pre-certification Missing Baseline PASI / LOINC Lab Score (>=12)", "RECOVERABLE_REVENUE_USD": 14200.00, "APPEAL_STATUS": "IN_REVIEW", "TERRITORY_ID": "US-PA-PHILLY-01"},
        {"DENIAL_ID": "PA-DEN-003", "CLAIM_ID": "CLM-PA-9184", "PATIENT_TOKEN": "PAT-TOK-1035", "PRESCRIBING_NPI": "1205948372", "NDC_CODE": "0074-1050-01", "DRUG_BRAND": "Skyrizi", "DENIAL_DATE": "2024-10-15", "REJECTION_CODE": "NCPDP-88", "REJECTION_REASON": "DMR Rejection: Prerequisite Generic Methotrexate Trial Not Documented", "RECOVERABLE_REVENUE_USD": 14200.00, "APPEAL_STATUS": "PEER_TO_PEER_SCHEDULED", "TERRITORY_ID": "US-PA-PHILLY-01"},
        {"DENIAL_ID": "PA-DEN-004", "CLAIM_ID": "CLM-PA-9185", "PATIENT_TOKEN": "PAT-TOK-1049", "PRESCRIBING_NPI": "1205948372", "NDC_CODE": "0074-1050-01", "DRUG_BRAND": "Skyrizi", "DENIAL_DATE": "2024-11-12", "REJECTION_CODE": "X12-50", "REJECTION_REASON": "Non-covered Specialty Benefit; Route via Specialty Pharmacy Network", "RECOVERABLE_REVENUE_USD": 14200.00, "APPEAL_STATUS": "OVERTURNED", "TERRITORY_ID": "US-PA-PHILLY-01"},
        {"DENIAL_ID": "PA-DEN-005", "CLAIM_ID": "CLM-PA-9186", "PATIENT_TOKEN": "PAT-TOK-1061", "PRESCRIBING_NPI": "1394019284", "NDC_CODE": "0074-1050-01", "DRUG_BRAND": "Skyrizi", "DENIAL_DATE": "2024-10-22", "REJECTION_CODE": "X12-75", "REJECTION_REASON": "Prior Authorization Required / Incomplete Clinical Chart Notes", "RECOVERABLE_REVENUE_USD": 14200.00, "APPEAL_STATUS": "IN_REVIEW", "TERRITORY_ID": "US-NE-T12"},
        {"DENIAL_ID": "PA-DEN-006", "CLAIM_ID": "CLM-PA-9187", "PATIENT_TOKEN": "PAT-TOK-1070", "PRESCRIBING_NPI": "1928374650", "NDC_CODE": "0074-1050-01", "DRUG_BRAND": "Skyrizi", "DENIAL_DATE": "2024-11-18", "REJECTION_CODE": "NCPDP-70", "REJECTION_REASON": "Formulary Tier 3 Exclusion without Exception Protocol", "RECOVERABLE_REVENUE_USD": 14200.00, "APPEAL_STATUS": "IN_REVIEW", "TERRITORY_ID": "US-PA-PHILLY-01"}
    ]
    df = pd.DataFrame(denials)
    df.to_csv(RAW_CSV_DIR / "fact_pa_denials.csv", index=False)
    print(f"[*] Generated {len(df)} PA Denial records.")
    return df

def generate_call_activity():
    calls = [
        {"CALL_ID": "CALL-001", "HCP_ID": "HCP-001", "REP_NAME": "Marcus Vance", "TERRITORY_ID": "US-PA-PHILLY-01", "CALL_DATE": "2024-11-14", "INTERACTION_TYPE": "In-Person Detailing", "DETAIL_PRIORITY": "UltIMMa-1 PASI 90 Superiority vs Ustekinumab", "SAMPLES_DROPPED_QTY": 2, "LOT_NUMBER": "LOT-SK-9812", "SIGNATURE_VERIFIED": "Y"},
        {"CALL_ID": "CALL-002", "HCP_ID": "HCP-002", "REP_NAME": "Marcus Vance", "TERRITORY_ID": "US-PA-PHILLY-01", "CALL_DATE": "2024-11-12", "INTERACTION_TYPE": "In-Person Detailing", "DETAIL_PRIORITY": "IMMvent Head-to-Head vs Adalimumab in Inadequate Responders", "SAMPLES_DROPPED_QTY": 2, "LOT_NUMBER": "LOT-SK-9812", "SIGNATURE_VERIFIED": "Y"},
        {"CALL_ID": "CALL-003", "HCP_ID": "HCP-004", "REP_NAME": "Marcus Vance", "TERRITORY_ID": "US-PA-PHILLY-01", "CALL_DATE": "2024-11-10", "INTERACTION_TYPE": "Medical Education Lunch", "DETAIL_PRIORITY": "Safety Profile & Infection Screening Protocols", "SAMPLES_DROPPED_QTY": 0, "LOT_NUMBER": "N/A", "SIGNATURE_VERIFIED": "Y"},
        {"CALL_ID": "CALL-004", "HCP_ID": "HCP-010", "REP_NAME": "Marcus Vance", "TERRITORY_ID": "US-PA-PHILLY-01", "CALL_DATE": "2024-11-05", "INTERACTION_TYPE": "In-Person Detailing", "DETAIL_PRIORITY": "Week 52 PASI 100 Complete Skin Clearance Maintenance", "SAMPLES_DROPPED_QTY": 4, "LOT_NUMBER": "LOT-SK-9815", "SIGNATURE_VERIFIED": "Y"}
    ]
    df = pd.DataFrame(calls)
    df.to_csv(RAW_CSV_DIR / "fact_call_activity.csv", index=False)
    print(f"[*] Generated {len(df)} Detailing Call Activity records.")
    return df

if __name__ == "__main__":
    print("[*] Generating production-grade synthetic pharma dataset...")
    df_hco = generate_mdm_hco()
    df_terr = generate_dim_territory()
    df_hcp = generate_mdm_hcp()
    generate_hcp_alignment(df_hcp)
    generate_formulary_coverage()
    generate_prescription_events()
    generate_pa_denials()
    generate_call_activity()
    print("[+] All synthetic pharma data files successfully written to data/raw_csv/.")
