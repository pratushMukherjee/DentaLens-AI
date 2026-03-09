"""Repository pattern for dental claims data access."""

import csv
from decimal import Decimal
from pathlib import Path

from dentalens.domain.enums import ClaimStatus, ProcedureCategory
from dentalens.domain.models.claim import Claim


# Map CDT code prefixes to procedure categories
_CODE_TO_CATEGORY: dict[str, ProcedureCategory] = {
    "D0": ProcedureCategory.DIAGNOSTIC,
    "D1": ProcedureCategory.PREVENTIVE,
    "D2": ProcedureCategory.RESTORATIVE,
    "D3": ProcedureCategory.ENDODONTIC,
    "D4": ProcedureCategory.PERIODONTIC,
    "D5": ProcedureCategory.PROSTHODONTIC,
    "D6": ProcedureCategory.PROSTHODONTIC,
    "D7": ProcedureCategory.ORAL_SURGERY,
    "D8": ProcedureCategory.ORTHODONTIC,
}


def _code_to_category(code: str) -> ProcedureCategory:
    prefix = code[:2]
    return _CODE_TO_CATEGORY.get(prefix, ProcedureCategory.DIAGNOSTIC)


class ClaimsRepository:
    """Abstracts dental claims data access behind a clean interface (Repository pattern)."""

    def __init__(self, data_path: Path):
        self._claims: list[Claim] = []
        self._load(data_path)

    def _load(self, path: Path) -> None:
        with open(path, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                self._claims.append(Claim(
                    claim_id=row["claim_id"],
                    patient_id=row["patient_id"],
                    provider_id=row["provider_id"],
                    procedure_code=row["procedure_code"],
                    procedure_description=row["procedure_description"],
                    date_of_service=row["date_of_service"],
                    billed_amount=Decimal(row["billed_amount"]),
                    allowed_amount=Decimal(row["allowed_amount"]),
                    paid_amount=Decimal(row["paid_amount"]),
                    patient_responsibility=Decimal(row["patient_responsibility"]),
                    claim_status=ClaimStatus(row["claim_status"]),
                    plan_id=row["plan_id"],
                    tooth_number=int(row["tooth_number"]) if row["tooth_number"] else None,
                    surface=row["surface"] if row["surface"] else None,
                    diagnosis_code=row["diagnosis_code"] if row["diagnosis_code"] else None,
                ))

    def get_all_claims(self) -> list[Claim]:
        return list(self._claims)

    def get_claim_by_id(self, claim_id: str) -> Claim | None:
        return next((c for c in self._claims if c.claim_id == claim_id), None)

    def get_claims_by_status(self, status: ClaimStatus) -> list[Claim]:
        return [c for c in self._claims if c.claim_status == status]

    def get_claims_by_procedure_category(self, category: ProcedureCategory) -> list[Claim]:
        return [c for c in self._claims if _code_to_category(c.procedure_code) == category]

    def get_claims_summary(self) -> dict:
        """Aggregate statistics across all claims."""
        total = len(self._claims)
        if total == 0:
            return {"total_claims": 0}

        total_billed = sum(c.billed_amount for c in self._claims)
        total_paid = sum(c.paid_amount for c in self._claims)
        status_counts = {}
        for c in self._claims:
            status_counts[c.claim_status.value] = status_counts.get(c.claim_status.value, 0) + 1

        category_counts = {}
        for c in self._claims:
            cat = _code_to_category(c.procedure_code).value
            category_counts[cat] = category_counts.get(cat, 0) + 1

        return {
            "total_claims": total,
            "total_billed": float(total_billed),
            "total_paid": float(total_paid),
            "avg_billed": float(total_billed / total),
            "avg_paid": float(total_paid / total),
            "approval_rate": status_counts.get("approved", 0) / total,
            "status_counts": status_counts,
            "category_counts": category_counts,
        }

    def detect_anomalies(self) -> list[dict]:
        """Flag claims with potential billing anomalies."""
        # Build typical cost ranges per procedure code
        code_amounts: dict[str, list[float]] = {}
        for c in self._claims:
            code_amounts.setdefault(c.procedure_code, []).append(float(c.billed_amount))

        code_stats: dict[str, tuple[float, float]] = {}
        for code, amounts in code_amounts.items():
            mean = sum(amounts) / len(amounts)
            std = (sum((x - mean) ** 2 for x in amounts) / len(amounts)) ** 0.5
            code_stats[code] = (mean, std)

        anomalies = []
        for c in self._claims:
            mean, std = code_stats[c.procedure_code]
            billed = float(c.billed_amount)
            if std > 0 and billed > mean + 2 * std:
                anomalies.append({
                    "claim_id": c.claim_id,
                    "procedure_code": c.procedure_code,
                    "billed_amount": billed,
                    "typical_mean": round(mean, 2),
                    "typical_std": round(std, 2),
                    "deviation": round((billed - mean) / std, 2),
                    "reason": f"Billed amount ${billed:.2f} exceeds typical range "
                              f"(mean ${mean:.2f}, +{((billed - mean) / std):.1f} std deviations)",
                })
        return anomalies
