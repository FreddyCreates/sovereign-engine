# Compliance Boundary

FSOS encodes compliance-inspired gates from the authored product plan and official FMCSA/eCFR reference points:

- broker record discipline: 49 CFR Part 371;
- HOS: 49 CFR Part 395;
- ELD: 49 CFR Part 395 Subpart B;
- insurance / financial responsibility: 49 CFR Part 387;
- broker financial responsibility fallback: 49 CFR 387.307.

## Important

This code is not legal advice. It is an operational control layer that makes compliance assumptions explicit and testable. Before live deployment, transportation counsel should review:

- bona fide agent contract posture;
- whether any FSOS workflow creates broker authority requirements;
- escrow and payment handling;
- QuickPay / factoring marketplace structure;
- UCC and tax automation;
- carrier data ownership and consent;
- HAZMAT and insurance minimums.

## Broker-Risk Guardrails

The current `evaluate_bona_fide_agent` gate blocks:

- no written contract;
- no long-term carrier relationship;
- direct shipper negotiation by the platform;
- platform handling shipper-to-carrier money.

If FSOS chooses a broker-mode fallback, the system must enforce the broker financial responsibility and authority path instead of using agent-mode language.

