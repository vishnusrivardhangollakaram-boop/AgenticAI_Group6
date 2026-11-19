"""Fictional placement-cycle data. All applicants, employers and notices are synthetic."""

AS_OF = "2026-11-19T09:30:00+05:30"
DEMO_CASES = ("PC-101", "PC-102", "PC-103")
DEMO_PROFILE = {
    "student_id": "STU-001",
    "student_name": "Asha Rao",
    "cgpa": 7.6,
    "cgpa_scale": 10,
    "experience_months": 18,
    "capstone": "Applied AI Lab",
    "capstone_credits": 4,
    "identity_scope": "verified",
}
TOOL_LABELS = {
    "read_profile": "Read candidate profile",
    "read_notice": "Read base role notice",
    "find_amendments": "Check official amendments",
    "verify_equivalence": "Check capstone equivalence",
}
REVIEW_DECISIONS = {
    "equivalent": "Confirm documented equivalence",
    "not_equivalent": "Record that equivalence is unconfirmed",
    "request_evidence": "Request more evidence",
}


def notice(identifier, title, employer, *, cgpa=7.0, months=12, capstone=None,
           deadline="2026-11-26T18:00:00+05:30", revision=1, published="2026-11-16"):
    return {
        "id": identifier, "role_title": title, "employer": employer,
        "revision": revision, "published": published, "min_cgpa": cgpa,
        "min_experience_months": months, "capstone_required": capstone,
        "deadline": deadline,
    }


def make_case(key, label, rule, expected, *, overrides=None, amendments=(),
              equivalence=None, demo=False, scoped=True):
    applicant = dict(DEMO_PROFILE, **(overrides or {}))
    if not scoped:
        applicant["identity_scope"] = "out_of_scope"
    return {
        "id": key, "title": label, "ticket": "Can I apply for the " + rule["role_title"] + " role?",
        "student_name": applicant["student_name"], "role_title": rule["role_title"],
        "employer": rule["employer"], "profile": applicant, "notice": rule,
        "amendments": list(amendments), "equivalence": equivalence,
        "expected": expected, "demo": demo, "as_of": AS_OF,
    }


PRODUCT = notice("PL-PA-01", "Product Analyst", "Mosaic Metrics")
BUSINESS = notice("PL-BA-01", "Business Analyst", "CedarBridge Advisory",
                  deadline="2026-11-27T18:00:00+05:30")
BUSINESS_AMENDMENT = notice("PL-BA-02", "Business Analyst", "CedarBridge Advisory",
                            months=24, deadline="2026-11-27T18:00:00+05:30",
                            revision=2, published="2026-11-18")
AI = notice("PL-AI-01", "AI Strategy Associate", "FableAxis Consulting", cgpa=7.5,
            months=15, capstone="AI Strategy Practicum",
            deadline="2026-11-28T18:00:00+05:30")
EQUIVALENCE_UNLISTED = {
    "id": "PL-EQ-01", "title": "Academic equivalence register", "revision": 1,
    "status": "unlisted",
    "text": "Applied AI Lab is unlisted for AI Strategy Practicum. Placement Office verification is required.",
}
EQUIVALENCE_CONFIRMED = {
    "id": "PL-EQ-02", "title": "Academic equivalence register", "revision": 2,
    "status": "accepted",
    "text": "Applied AI Lab is a verified equivalent of AI Strategy Practicum for this role.",
}
EQUIVALENCE_REJECTED = {
    "id": "PL-EQ-03", "title": "Academic equivalence register", "revision": 2,
    "status": "rejected",
    "text": "Applied AI Lab does not satisfy AI Strategy Practicum for this role.",
}

CASES = {
    item["id"]: item for item in (
        make_case("PC-101", "Clearly ready", PRODUCT, "ready", demo=True),
        make_case("PC-102", "Notice changed eligibility", BUSINESS, "not_ready",
                  amendments=(BUSINESS_AMENDMENT,), demo=True),
        make_case("PC-103", "Capstone equivalence unresolved", AI, "needs_review",
                  equivalence=EQUIVALENCE_UNLISTED, demo=True),
        make_case("EV-01", "Valid listing; requirements met", PRODUCT, "ready"),
        make_case("EV-02", "Amended experience threshold", BUSINESS, "not_ready",
                  amendments=(BUSINESS_AMENDMENT,)),
        make_case("EV-03", "Unlisted equivalence", AI, "needs_review",
                  equivalence=EQUIVALENCE_UNLISTED),
        make_case("EV-04", "Verified equivalence", AI, "ready", equivalence=EQUIVALENCE_CONFIRMED),
        make_case("EV-05", "Equivalence ruled out", AI, "not_ready", equivalence=EQUIVALENCE_REJECTED),
        make_case("EV-06", "Exact capstone", AI, "ready",
                  overrides={"capstone": "AI Strategy Practicum"}),
        make_case("EV-07", "Closed application window",
                  dict(PRODUCT, deadline="2026-11-18T18:00:00+05:30"), "closed"),
        make_case("EV-08", "CGPA evidence missing", PRODUCT, "missing_evidence",
                  overrides={"cgpa": None}),
        make_case("EV-09", "CGPA below minimum", PRODUCT, "not_ready", overrides={"cgpa": 6.8}),
        make_case("EV-10", "Same revision, conflicting sources", BUSINESS, "needs_review",
                  amendments=(BUSINESS_AMENDMENT, dict(BUSINESS_AMENDMENT, id="PL-BA-02B",
                                                       min_experience_months=15))),
        make_case("EV-11", "Future amendment excluded", BUSINESS, "ready",
                  amendments=(dict(BUSINESS_AMENDMENT, published="2026-11-21"),)),
        make_case("EV-12", "Profile not in case scope", PRODUCT, "missing_evidence", scoped=False),
        make_case("EV-13", "Insufficient experience before capstone check", AI, "not_ready",
                  overrides={"experience_months": 9}, equivalence=EQUIVALENCE_UNLISTED),
        make_case("EV-14", "Amendment extends expired deadline",
                  dict(BUSINESS, deadline="2026-11-18T18:00:00+05:30"), "ready",
                  amendments=(dict(BUSINESS_AMENDMENT, min_experience_months=12),)),
    )
}
