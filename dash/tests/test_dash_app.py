from unittest import (
    mock,
    TestCase,
)

from app import *

class TestDashApp(TestCase):

    def test_format_ts(self):
        """Test epoch to PST conversion"""
        epoch = 1587830400
        formatted_ts = 'Sat 4/25 4:00PM PST'
        
        assert formatted_ts == format_ts(epoch)


    def test_get_status_over_time(self):
        """Test status caluclations on fake data"""
        BASE = 1500000000
        data = {
            'received_at': [BASE, BASE + 400, BASE + 400, BASE + 1500],
            'started_at': [BASE+5, BASE + 500, BASE + 700, BASE + 1501],
            'completed_at': [BASE+700, BASE + 700, BASE + 700, BASE + 1502],
        }
        df = pd.DataFrame(data)

        expected_df = pd.DataFrame(
            {
                'Queued': [1, 1, 0],
                'In Progress': [0, 2, 0],
            }, index = pd.to_datetime(
                [1500000000, 1500000600, 1500001200],
                unit='s',
            )
        )

        actual_df = get_status_over_time(df)
        assert actual_df.equals(expected_df)
