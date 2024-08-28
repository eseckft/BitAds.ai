import unittest
from unittest.mock import MagicMock
from parameterized import parameterized

from common.formula import process_aggregation
from common.schemas.aggregated import AggregationSchema


class TestFormula(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.aggregation_schema = MagicMock(spec=AggregationSchema)

    @parameterized.expand([
        (
                1000, 900, 100, 100, 0.01, 0.3, 0.2, 0.4, 0.1, 1000, 0.6571
        ),
        (
                1000, 1000, 0, 1000, 0.2, 0.5, 0.4, 0.3, 0.2, 1000, 0.27
        ),
        (
                1000, 0, 1000, 1000, 0.2, 0.5, 0.4, 0.3, 0.2, 1000, 0
        ),
        (
                800, 500, 300, 50, 0.2, 0.3, 0.4, 0.2, 0.1, 1000, 0.0555
        ),
        (
                1000, 800, 600, 160, 0.2, 0.3, 0.4, 0.2, 0.1, 1000, 0
        ),
        (
                500, 300, 200, 45, 0.2, 0.3, 0.4, 0.2, 0.1, 1000, 0.0459
        ),
        (
                0, 0, 0, 0, 0.2, 0.3, 0.4, 0.2, 0.1, 1000, 0
        ),
        (
                1500, 1200, 1000, 240, 0.2, 0.3, 0.4, 0.2, 0.1, 1000, 0
        ),
        (
                700, 600, 450, 90, 0.2, 0.3, 0.4, 0.2, 0.1, 1000, 0
        ),
        (
            # Rounding test data
            900, 700, 500, 140, 0.2, 0.3, 0.4, 0.2, 0.1, 1000, 0.09524
        ),
        (
            700, 450, 300, 67, 0.2, 0.3, 0.4, 0.2, 0.1, 1000, 0.05873
        )


    ])
    def test_process_aggregation_happy_path(self, visits, visits_unique, at, count_through_rate_click, CTRmax,
                                            Wots, Wuvps, Wuv, Wctr, UVmax, expected_result) -> None:
        aggregation_mock = self.aggregation_schema
        aggregation_mock.count_through_rate_click = count_through_rate_click
        aggregation_mock.visits = visits
        aggregation_mock.visits_unique = visits_unique
        aggregation_mock.at = at

        actual_result = process_aggregation(aggregation_mock, CTRmax, Wots, Wuvps, Wuv, Wctr, UVmax)
        self.assertEqual(expected_result, actual_result)

    @parameterized.expand([
        (
                1000, 900, 100, 100, 0.01, 0.3, 0.2, 0.4, 0.1, 1000
        )
    ])
    def test_process_aggregation_type_error(self, visits, visits_unique, at, count_through_rate_click, CTRmax,
                                            Wots, Wuvps, Wuv, Wctr, UVmax):
        aggregation_mock = self.aggregation_schema
        aggregation_mock.count_through_rate_click = count_through_rate_click
        aggregation_mock.visits = visits
        aggregation_mock.visits_unique = visits_unique
        aggregation_mock.at = at
        actual_result = process_aggregation(aggregation_mock, CTRmax, Wots, Wuvps, Wuv, Wctr, UVmax)
        for var in locals().values():
            str(var)
            test_result = process_aggregation(aggregation_mock, CTRmax, Wots, Wuvps, Wuv, Wctr, UVmax)
            with self.assertRaises(Exception) as context:
                self.assertEqual(context.exception, test_result)


if __name__ == '__main__':
    unittest.main()
