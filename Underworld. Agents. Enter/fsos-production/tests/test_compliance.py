from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal
import unittest

from fsos.compliance import evaluate_bona_fide_agent, evaluate_hos, evaluate_load_access
from fsos.demo import demo_carrier, demo_hos, demo_load
from fsos.models import AgentAgreement, HOSStatus


class ComplianceTests(unittest.TestCase):
    def test_demo_load_is_allowed(self) -> None:
        decision = evaluate_load_access(demo_carrier(), demo_hos(), demo_load())
        self.assertTrue(decision.allowed, [issue.code for issue in decision.issues])

    def test_hos_blocks_dispatch_halt(self) -> None:
        hos = HOSStatus(
            driver_id="driver-001",
            driving_hours_today=Decimal("10.6"),
            on_duty_hours_today=Decimal("11"),
            on_duty_hours_8_days=Decimal("40"),
            off_duty_hours_before_shift=Decimal("10"),
            eld_connected=True,
        )
        decision = evaluate_hos(hos, demo_load())
        self.assertFalse(decision.allowed)
        self.assertIn("DISPATCH_HALT", [issue.code for issue in decision.issues])

    def test_bona_fide_agent_blocks_money_handling(self) -> None:
        agreement = AgentAgreement(
            agreement_id="a1",
            carrier_id="c1",
            effective_at=datetime.now(timezone.utc),
            expires_at=datetime.now(timezone.utc) + timedelta(days=365),
            written_contract=True,
            long_term_relationship=True,
            negotiates_with_shipper=False,
            handles_shipper_carrier_money=True,
            compensation_payer="carrier",
        )
        decision = evaluate_bona_fide_agent(agreement)
        self.assertFalse(decision.allowed)
        self.assertIn("BROKER_RISK_MONEY_HANDLING", [issue.code for issue in decision.issues])


if __name__ == "__main__":
    unittest.main()

