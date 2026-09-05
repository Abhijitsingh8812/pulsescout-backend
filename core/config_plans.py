"""
Authoritative Subscription Plans Catalog for PulseScout.
Prices are stored in paise (1 INR = 100 paise).
Duration is in days.
"""

PLANS = {
    "gold_monthly": {
        "id": "gold_monthly",
        "name": "Gold Monthly",
        "tier": "gold",
        "billing_cycle": "monthly",
        "amount": 9900,  # ₹99 in paise
        "currency": "INR",
        "duration_days": 30
    },
    "gold_yearly": {
        "id": "gold_yearly",
        "name": "Gold Yearly",
        "tier": "gold",
        "billing_cycle": "yearly",
        "amount": 99900,  # ₹999 in paise
        "currency": "INR",
        "duration_days": 365
    }
}


def get_plan(plan_id: str) -> dict | None:
    if not plan_id:
        return None
    return PLANS.get(plan_id.lower())
