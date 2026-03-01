"""Embedded knowledge base for procurement policy agent."""

PROCUREMENT_POLICY = """
## Procurement Policy (POL-001 to POL-004)

**Spend Thresholds & Approval Requirements (POL-001):**
- Under $5,000: P-card allowed for eligible categories
- $5,000–$25,000: Purchase Order (PO) required, single approver (Manager)
- $25,000–$100,000: PO required, two approvers (Manager + Director)
- $100,000–$250,000: Competitive bids required (minimum 2 quotes), VP approval
- Over $250,000: Formal sourcing event (RFQ/RFP), Legal review, VP+ approval

**P-Card Usage (POL-002):**
P-cards MAY be used for: office supplies, software subscriptions under $5k/year, training under $2k, travel, professional services under $5k.
P-cards may NOT be used for: hardware over $1k, software with data access (PII/PHI), recurring subscriptions over $5k/year, or any purchase requiring a contract.

**Competitive Bidding (POL-003):**
Required for: (1) Single purchase over $100,000, (2) Services over $50,000, (3) Software/SaaS over $25,000/year. Minimum 2 written quotes. Document rationale if single source.

**Software & SaaS (POL-004):**
- Security review if PII/PHI/financial data
- Legal review if non-standard contract terms
- IT approval for integrations
- Under $5k/year: P-card if no data access
- $5k–$25k: PO + Security questionnaire
- Over $25k: Full procurement process
"""

SUPPLIER_ONBOARDING = """
## Supplier Onboarding Process

**Step 1 - Submit New Vendor Request:**
Complete New Vendor Request form in procurement portal. Include: vendor name, contact, category, estimated spend, business justification.

**Step 2 - Required Documentation:**
- W-9 or W-8BEN (tax)
- Certificate of Insurance: General Liability $1M, Professional Liability $1M if services
- ACH/banking details
- Signed NDA if confidential
- Security questionnaire if handling data

**Step 3 - Approvals:**
Requester's Manager → Category Lead → Procurement. Over $100k annual: add Finance. Data-handling vendors: add Security & Legal.

**Step 4 - SLA Expectations:**
- Standard: 5 business days for complete packages
- Incomplete: 2 business days to request missing items
- Expedited: 2 business days, requires VP approval
"""

SPEND_THRESHOLDS = [
    {"min": 0, "max": 5000, "method": "P-card", "approvers": "Cardholder"},
    {"min": 5000, "max": 25000, "method": "Purchase Order", "approvers": "Manager"},
    {"min": 25000, "max": 100000, "method": "Purchase Order", "approvers": "Manager + Director"},
    {"min": 100000, "max": 250000, "method": "Competitive Bids", "approvers": "Director + VP"},
    {"min": 250000, "max": None, "method": "Formal Sourcing (RFQ/RFP)", "approvers": "VP + Legal"},
]

TEMPLATE_GUIDE = """
## Templates

**SOW (Statement of Work):** Project-based services; deliverables and milestones. Mandatory: Scope, Deliverables, Timeline, Pricing, Acceptance criteria. Link: /templates/sow-template.docx

**MSA (Master Service Agreement):** Ongoing vendor relationship; framework for multiple SOWs. Mandatory: Term, Payment terms, Limitation of liability, Termination, IP ownership. Link: /templates/msa-template.docx

**NDA:** Before sharing confidential info; vendor evaluations. Mandatory: Definition of confidential info, Term, Return of materials. Link: /templates/nda-template.docx

**Intake required:** Business justification, Category, Estimated spend, Urgency, Data sensitivity (if applicable)
"""

ESCALATIONS = {
    "legal_review": ["Contract terms", "MSA/SOW", "Over $100k", "Indemnification"],
    "security_review": ["PII/PHI data", "Software integrations", "Cloud services"],
    "finance_review": ["Over $250k", "Multi-year commitment", "Payment terms > 30 days"],
}
