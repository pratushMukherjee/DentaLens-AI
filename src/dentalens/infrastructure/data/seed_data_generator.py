"""Generates synthetic dental claims data for development and demonstration."""

import csv
import json
import random
from datetime import date, timedelta
from pathlib import Path

# Procedure definitions: (code, description, category, min_billed, max_billed)
PROCEDURES = [
    ("D0120", "Periodic oral evaluation", "diagnostic", 35, 75),
    ("D0150", "Comprehensive oral evaluation", "diagnostic", 50, 120),
    ("D0210", "Full mouth X-rays", "diagnostic", 80, 200),
    ("D0274", "Bitewing X-rays (4 films)", "diagnostic", 40, 80),
    ("D1110", "Adult prophylaxis (cleaning)", "preventive", 75, 200),
    ("D1120", "Child prophylaxis (cleaning)", "preventive", 50, 120),
    ("D2140", "Amalgam filling - 1 surface", "restorative", 75, 150),
    ("D2391", "Composite filling - 1 surface posterior", "restorative", 100, 250),
    ("D2392", "Composite filling - 2 surfaces posterior", "restorative", 130, 300),
    ("D2740", "Crown - porcelain/ceramic", "prosthodontic", 800, 1500),
    ("D2750", "Crown - porcelain fused to metal", "prosthodontic", 850, 1400),
    ("D3310", "Root canal - anterior", "endodontic", 400, 900),
    ("D3320", "Root canal - premolar", "endodontic", 500, 1100),
    ("D3330", "Root canal - molar", "endodontic", 700, 1400),
    ("D4341", "Periodontal scaling - per quadrant", "periodontic", 150, 350),
    ("D7140", "Extraction - erupted tooth", "oral_surgery", 75, 250),
    ("D7210", "Surgical extraction", "oral_surgery", 150, 400),
    ("D5110", "Complete denture - maxillary", "prosthodontic", 1000, 2500),
    ("D8080", "Comprehensive orthodontic - adolescent", "orthodontic", 3000, 7000),
]

PLAN_IDS = ["DD-PPO-GOLD-2024", "DD-PPO-SILVER-2024", "DD-HMO-BASIC-2024"]

# Coverage rules by plan and category
COVERAGE_RULES: dict[str, dict[str, float]] = {
    "DD-PPO-GOLD-2024": {
        "diagnostic": 1.0, "preventive": 1.0, "restorative": 0.8,
        "endodontic": 0.8, "periodontic": 0.8, "prosthodontic": 0.5,
        "oral_surgery": 0.8, "orthodontic": 0.5,
    },
    "DD-PPO-SILVER-2024": {
        "diagnostic": 1.0, "preventive": 1.0, "restorative": 0.7,
        "endodontic": 0.7, "periodontic": 0.7, "prosthodontic": 0.4,
        "oral_surgery": 0.7, "orthodontic": 0.0,
    },
    "DD-HMO-BASIC-2024": {
        "diagnostic": 1.0, "preventive": 1.0, "restorative": 0.85,
        "endodontic": 0.75, "periodontic": 0.8, "prosthodontic": 0.6,
        "oral_surgery": 0.85, "orthodontic": 0.4,
    },
}

STATUSES = ["approved", "approved", "approved", "approved", "approved",
            "approved", "approved", "pending", "denied", "submitted"]


def generate_synthetic_claims(n: int = 1200, output_path: Path | None = None) -> list[dict]:
    """Generate n synthetic dental claims with ~5% anomalies."""
    random.seed(42)
    patient_ids = [f"PAT-{i:04d}" for i in range(1, 51)]
    provider_ids = [f"PROV-{i:03d}" for i in range(1, 21)]
    start_date = date(2024, 1, 1)
    end_date = date(2024, 12, 31)
    date_range = (end_date - start_date).days

    claims = []
    for i in range(1, n + 1):
        proc = random.choice(PROCEDURES)
        code, desc, category, min_cost, max_cost = proc
        plan_id = random.choice(PLAN_IDS)
        coverage_pct = COVERAGE_RULES[plan_id][category]
        billed = round(random.uniform(min_cost, max_cost), 2)

        # ~5% anomalous claims: inflated billing
        is_anomalous = random.random() < 0.05
        if is_anomalous:
            billed = round(billed * random.uniform(2.5, 4.0), 2)

        allowed = round(billed * random.uniform(0.75, 0.95), 2)
        paid = round(allowed * coverage_pct, 2)
        patient_resp = round(allowed - paid, 2)
        status = random.choice(STATUSES)

        if is_anomalous and random.random() < 0.6:
            status = "denied"

        service_date = start_date + timedelta(days=random.randint(0, date_range))
        tooth = random.randint(1, 32) if category not in ("diagnostic", "preventive", "orthodontic") else None

        claim = {
            "claim_id": f"CLM-{i:06d}",
            "patient_id": random.choice(patient_ids),
            "provider_id": random.choice(provider_ids),
            "procedure_code": code,
            "procedure_description": desc,
            "date_of_service": service_date.isoformat(),
            "billed_amount": billed,
            "allowed_amount": allowed,
            "paid_amount": paid,
            "patient_responsibility": patient_resp,
            "claim_status": status,
            "plan_id": plan_id,
            "tooth_number": tooth,
            "surface": random.choice(["M", "D", "B", "L", "O", None]) if category == "restorative" else None,
            "diagnosis_code": None,
        }
        claims.append(claim)

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=claims[0].keys())
            writer.writeheader()
            writer.writerows(claims)

    return claims


def generate_providers(output_path: Path) -> list[dict]:
    """Generate synthetic provider directory."""
    providers = []
    names = [
        "Bright Smile Dental", "Okemos Family Dentistry", "Capital City Dental Care",
        "Meridian Dental Group", "Lansing Oral Health Center", "East Lansing Dental",
        "Grand River Dental", "Haslett Family Dental", "Delta Township Dentistry",
        "Williamston Dental Care", "Mason Family Dental", "DeWitt Dental Associates",
        "Holt Dental Center", "Bath Township Dental", "Laingsburg Dental Care",
        "Perry Family Dentistry", "St. Johns Dental Group", "Charlotte Dental Care",
        "Eaton Rapids Dental", "Portland Family Dental",
    ]
    for i, name in enumerate(names, 1):
        providers.append({
            "provider_id": f"PROV-{i:03d}",
            "name": name,
            "npi": f"1{random.randint(100000000, 999999999)}",
            "network": random.choice(["PPO", "PPO", "HMO", "PPO"]),
            "city": random.choice(["Okemos", "Lansing", "East Lansing", "Meridian Township"]),
            "state": "MI",
            "accepting_new_patients": random.choice([True, True, True, False]),
        })
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump({"providers": providers}, f, indent=2)
    return providers


if __name__ == "__main__":
    base = Path("data/seed")
    print("Generating synthetic claims...")
    claims = generate_synthetic_claims(1200, base / "claims" / "synthetic_claims.csv")
    print(f"  Generated {len(claims)} claims")

    print("Generating provider directory...")
    providers = generate_providers(base / "claims" / "providers.json")
    print(f"  Generated {len(providers)} providers")

    print("Done! Seed data is ready.")
