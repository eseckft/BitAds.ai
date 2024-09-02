import unittest
from unittest.mock import MagicMock
from parameterized import parameterized

from common.formula import process_cpa
from common.schemas.aggregated import AggregationSchema


class TestFormula(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.aggregation_schema = MagicMock(spec=AggregationSchema)

    @parameterized.expand([
        (5, 5000, 0, 500, 0, 0.606),
        (5, 5000, 0, 500, 0.48837, 0.60649),
        (0, 5000, 0, 0, 0.48837, 0.00049),
        (5, 5000, 1, 500, 0, 0),
        (0, 5000, 0, 0, 0, 0),
        (1, 1000, 0, 100, 0, 0.126),
        (2, 1500, 0, 200, 0.126, 0.24813),
        (3, 2000, 0, 300, 0.24813, 0.36925),
        (100, 10_000, 1, 1000, 0, 0.66),
        (50, 2000, 5, 500, 0.5, 0.7505),              # Moderate sales, average MR, some refunds
        (0, 5000, 0, 0, 0.2, 0.0002),                 # No sales
        (10, 100, 0, 100, 0.1, 0.4201),                 # Low sales, low MR, no refunds
        (250, 500, 50, 500, 1.0, 0.0),              # High sales, high refunds (penalty)
        (500, 1000, 99, 500, 0.9, 0.9009),            # Maximum normalized values
        # Edge cases
        (0, 1, 0, 0, 0.0, 0),                 # Edge case: no visits, no sales, no MR
        (0, 5000, 0, 0, 0.2, 0.0002),            # No sales, low MR
        (10, 100, 0, 100, 0.1, 0.4201),            # Low sales, low MR, no refunds
        (250, 500, 50, 500, 1.0, 0),         # High sales, high refunds (penalty)
        (500, 1000, 99, 500, 0.9, 0.9009),       # Maximum normalized values, high MR

    ])
    def test_process_cpa_happy_path(self, total_sales, visits, total_refunds, sales_amount, MR,
                                    expected_result) -> None:
        Wsales = 0.6
        Wcr = 0.3
        Wmr = 0.1
        SALESmax = 500
        CRmax = 0.05
        MRmax = 100

        aggregation_mock = self.aggregation_schema
        aggregation_mock.total_sales = total_sales
        aggregation_mock.visits = visits
        aggregation_mock.total_refunds = total_refunds
        aggregation_mock.sales_amount = sales_amount

        actual_result = process_cpa(aggregation_mock, MR, SALESmax, CRmax, MRmax, Wsales, Wcr, Wmr)
        self.assertEqual(expected_result, actual_result)

    @parameterized.expand([
        (5, 5000, 0, 500, 0, 0.181)
    ])
    def test_process_cpa_with_no_data_then_sad_path(self, total_sales, visits, total_refunds, sales_amount, MR,
                                                    expected_result) -> None:
        Wsales = 0.6
        Wcr = 0.3
        Wmr = 0.1
        SALESmax = 500
        CRmax = 0.05
        MRmax = 100

        aggregation_mock = self.aggregation_schema
        aggregation_mock.count_through_rate_click = total_sales
        aggregation_mock.visits = visits
        aggregation_mock.visits_unique = total_refunds
        aggregation_mock.at = sales_amount

        for var in locals().values():
            var = None
            test_result = process_cpa(aggregation_mock, MR, SALESmax, CRmax, MRmax, Wsales, Wcr, Wmr)
            with self.assertRaises(Exception) as context:
                print(context.exception)
                self.assertEqual(context.exception, test_result)

    @parameterized.expand([
        (5, 5000, 0, 500, 0, 0.181)
    ])
    def test_process_cpa_with_incorrect_types_then_type_error(self, total_sales, visits, total_refunds, sales_amount,
                                                              MR, expected_result) -> None:
        Wsales = 0.6
        Wcr = 0.3
        Wmr = 0.1
        SALESmax = 500
        CRmax = 0.05
        MRmax = 100

        aggregation_mock = self.aggregation_schema
        aggregation_mock.count_through_rate_click = total_sales
        aggregation_mock.visits = visits
        aggregation_mock.visits_unique = total_refunds
        aggregation_mock.at = sales_amount

        for var in locals().values():
            str(var)
            test_result = process_cpa(aggregation_mock, MR, SALESmax, CRmax, MRmax, Wsales, Wcr, Wmr)
            with self.assertRaises(Exception) as context:
                self.assertEqual(context.exception, test_result)


if __name__ == '__main__':
    unittest.main()
