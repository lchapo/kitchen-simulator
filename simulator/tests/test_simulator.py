from unittest import (
    mock,
    TestCase,
)

from order_simulator import *

class TestCommon(TestCase):

    def test_get_time_full_seconds(self):
        """Test string to epoch conversion"""
        ts = '2020-04-25T16:00:00'
        ts_epoch = 1587830400
        assert ts_epoch == get_time(ts)


    def test_get_time_fractional_seconds(self):
        """Fractional second should be truncated"""
        ts = '2020-04-25T16:00:00.31415926535'
        ts_epoch = 1587830400
        assert ts_epoch == get_time(ts)


    def test_regular_order_processed(self):
        """Order should be received and completed"""
        with mock.patch('order_simulator.update_db_order_received') as order_received, \
                mock.patch('order_simulator.update_db_order_completed') as order_completed, \
                mock.patch('order_simulator.css_cursor'):
            order = {
                'items': [
                    {'name': 'Puff Pastry Chicken Potpie', 'price_per_unit': 1, 'quantity': 1}
                ],
                'name': 'Testy McTestFace',
                'service': 'SoTesty',
                'ordered_at': '2019-02-18T16:01:00'
            }
            simulate_orders([order])
            order_received.assert_called_once()
            order_completed.assert_called_once()


    def test_empty_order_not_processed(self):
        """An empty order should not be processed"""
        with mock.patch('order_simulator.update_db_order_received') as order_received, \
                mock.patch('order_simulator.update_db_order_completed') as order_completed, \
                mock.patch('order_simulator.css_cursor'):
            empty_order = {
                'items': [],
                'name': 'Testy McTestFace',
                'service': 'SoTesty',
                'ordered_at': '2019-02-18T16:01:00'
            }
            simulate_orders([empty_order])
            order_received.assert_not_called()
            order_completed.assert_not_called()
