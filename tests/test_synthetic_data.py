import unittest

import pandas as pd

from mansoura_mobility import (
    SimulationConfig,
    generate_synthetic_dataset,
    validation_report,
)


def small_config(seed: int = 17) -> SimulationConfig:
    return SimulationConfig(
        seed=seed,
        passenger_count=80,
        driver_count=15,
        dual_role_count=5,
        offer_count=500,
        simulation_days=30,
    )


class SyntheticDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.dataset = generate_synthetic_dataset(small_config())

    def test_generated_dataset_passes_validation(self) -> None:
        report = validation_report(self.dataset)

        self.assertTrue(report["passed"].all())
        self.assertEqual(len(self.dataset.tables["offers"]), 500)
        self.assertEqual(len(self.dataset.tables["zones"]), 15)
        self.assertEqual(len(self.dataset.tables["zone_routes"]), 210)

    def test_generation_is_deterministic(self) -> None:
        first = generate_synthetic_dataset(small_config(seed=91))
        second = generate_synthetic_dataset(small_config(seed=91))

        for table_name in first.tables:
            pd.testing.assert_frame_equal(
                first.tables[table_name],
                second.tables[table_name],
                check_dtype=True,
            )

    def test_rides_only_use_accepted_offers(self) -> None:
        offers = self.dataset.tables["offers"].set_index("offer_id")
        rides = self.dataset.tables["rides"]

        statuses = offers.loc[rides["offer_id"], "offer_status"]
        self.assertTrue(statuses.eq("ACCEPTED").all())
        self.assertTrue(rides["offer_id"].is_unique)

    def test_refunds_never_exceed_capture(self) -> None:
        payments = self.dataset.tables["payment_attempts"].set_index(
            "payment_attempt_id"
        )
        refunds = self.dataset.tables["refunds"]

        for refund in refunds.itertuples(index=False):
            captured = payments.loc[
                refund.payment_attempt_id, "captured_amount_egp"
            ]
            self.assertTrue(pd.notna(captured))
            self.assertLessEqual(refund.refund_amount_egp, captured)


if __name__ == "__main__":
    unittest.main()
