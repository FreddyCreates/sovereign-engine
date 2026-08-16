from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from fsos.audit import AuditLog
from fsos.demo import demo_carrier, demo_hos, demo_load
from fsos.matching import score_load_match
from fsos.models import PaymentMode
from fsos.payments import settlement_for_load


class PaymentsMatchingAuditTests(unittest.TestCase):
    def test_quickpay_fee_split(self) -> None:
        settlement = settlement_for_load(
            settlement_id="s1",
            load_id="l1",
            carrier_id="c1",
            shipper_id="w1",
            gross_amount_usd=Decimal("1000"),
            payment_mode=PaymentMode.QUICKPAY_ONE_DAY,
            prior_shipper_carrier_transactions=0,
        )
        self.assertEqual(settlement.platform_fee_usd, Decimal("3.09"))
        self.assertEqual(settlement.liquidity_provider_fee_usd, Decimal("3.09"))
        self.assertEqual(settlement.carrier_receives_usd, Decimal("993.82"))
        self.assertTrue(settlement.escrow_required)

    def test_match_demo_carrier(self) -> None:
        result = score_load_match(demo_carrier(), demo_hos(), demo_load())
        self.assertTrue(result.allowed)
        self.assertGreater(result.score, Decimal("0"))

    def test_audit_hash_chain(self) -> None:
        with TemporaryDirectory() as tmp:
            log = AuditLog(Path(tmp) / "audit.jsonl")
            log.append("carrier.verified", "system", {"carrier_id": "c1"})
            log.append("load.matched", "system", {"load_id": "l1"})
            self.assertTrue(log.verify())


if __name__ == "__main__":
    unittest.main()

