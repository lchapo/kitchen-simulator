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

	# # def test_empty_order():
	# 	"""An empty order should not be processed"""
