import unittest

from common.schemas.aggregated import AggregationSchema

from common.formula import process_cpa


class TestProcessCPA(unittest.TestCase):
    def test_typical_case(self):
        aggregation = AggregationSchema(
            visits=100,
            visits_unique=80,
            at=150,
            count_through_rate_click=50,
            total_sales=20,
            total_refunds=2,
            sales_amount=1000.0,
        )
        result = process_cpa(
            aggregation,
            MR=0.5,
            SALESmax=2000.0,
            CRmax=0.3,
            MRmax=0.6,
            Wsales=0.4,
            Wcr=0.3,
            Wmr=0.3,
        )
        expected = round(
            (((0.4 * 0.5) + (0.3 * (20 / 100) / 0.3) + (0.3 * (0.5 / 0.6))) * 1.0), 5
        )
        self.assertEqual(expected, result)

    def test_zero_visits_but_rating_exists(self):
        aggregation = AggregationSchema(
            visits=0,
            visits_unique=0,
            at=0,
            count_through_rate_click=0,
            total_sales=0,
            total_refunds=0,
            sales_amount=0.0,
        )
        result = process_cpa(
            aggregation,
            MR=0.5,
            SALESmax=2000.0,
            CRmax=0.3,
            MRmax=0.6,
            Wsales=0.4,
            Wcr=0.3,
            Wmr=0.3,
        )
        expected = 0.25  # CR and all other metrics should be zero
        self.assertEqual(expected, result)

    def test_refunds_above_threshold(self):
        aggregation = AggregationSchema(
            visits=100,
            visits_unique=80,
            at=150,
            count_through_rate_click=50,
            total_sales=20,
            total_refunds=5,
            sales_amount=1000.0,
        )
        result = process_cpa(
            aggregation,
            MR=0.5,
            SALESmax=2000.0,
            CRmax=0.3,
            MRmax=0.6,
            Wsales=0.4,
            Wcr=0.3,
            Wmr=0.3,
        )
        expected = 0.0  # RP is 0.25, so RF should be 0.0, leading to a rating of 0.0
        self.assertEqual(expected, result)

    def test_sales_normalization(self):
        aggregation = AggregationSchema(
            visits=100,
            visits_unique=80,
            at=150,
            count_through_rate_click=50,
            total_sales=20,
            total_refunds=0,
            sales_amount=3000.0,  # Above SALESmax, should be capped at 1.0
        )
        result = process_cpa(
            aggregation,
            MR=0.5,
            SALESmax=2000.0,
            CRmax=0.3,
            MRmax=0.6,
            Wsales=0.4,
            Wcr=0.3,
            Wmr=0.3,
        )
        expected = round(
            (((0.4 * 1.0) + (0.3 * (20 / 100) / 0.3) + (0.3 * (0.5 / 0.6))) * 1.0), 5
        )
        self.assertEqual(expected, result)

    def test_edge_case_rounding(self):
        aggregation = AggregationSchema(
            visits=100,
            visits_unique=80,
            at=150,
            count_through_rate_click=50,
            total_sales=20,
            total_refunds=1,
            sales_amount=1999.99,
        )
        result = process_cpa(
            aggregation,
            MR=0.5,
            SALESmax=2000.0,
            CRmax=0.3,
            MRmax=0.6,
            Wsales=0.4,
            Wcr=0.3,
            Wmr=0.3,
            ndigits=7,
        )
        expected = round(
            (((0.4 * 0.999995) + (0.3 * (20 / 100) / 0.3) + (0.3 * (0.5 / 0.6))) * 1.0),
            7,
        )
        self.assertEqual(expected, result)


if __name__ == "__main__":
    unittest.main()
