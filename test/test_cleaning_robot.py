from unittest import TestCase
from unittest.mock import Mock, patch, call

from mock import GPIO
from mock.ibs import IBS
from src.cleaning_robot import CleaningRobot


class TestCleaningRobot(TestCase):

    def test_initialize_robot(self):
        sut = CleaningRobot()
        sut.initialize_robot()
        self.assertEqual(0, sut.pos_x)
        self.assertEqual(0, sut.pos_y)
        self.assertEqual('N', sut.heading)