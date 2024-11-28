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
        self.assertEqual(sut.N, sut.heading)

    def test_robot_status(self):
        sut = CleaningRobot()
        sut.pos_x = 1
        sut.pos_y = 3
        sut.heading = sut.W
        status = sut.robot_status()
        self.assertEqual("(1,3,W)", status)

    @patch.object(IBS, 'get_charge_left')
    @patch.object(GPIO, 'output')
    def test_manage_cleaning_system_charge_above_10(self, mock_gpio: Mock, mock_get_charge_left: Mock):
        mock_get_charge_left.return_value = 11
        sut = CleaningRobot()
        sut.manage_cleaning_system()
        self.assertTrue(sut.cleaning_system_on)
        self.assertFalse(sut.recharge_led_on)
        output_calls =[call(sut.CLEANING_SYSTEM_PIN, True), call(sut.RECHARGE_LED_PIN, False)]
        mock_gpio.assert_has_calls(output_calls)

    @patch.object(IBS, 'get_charge_left')
    @patch.object(GPIO, 'output')
    def test_manage_cleaning_system_charge_less_or_equal_10(self, mock_gpio: Mock, mock_get_charge_left: Mock):
        mock_get_charge_left.return_value = 10
        sut = CleaningRobot()
        sut.manage_cleaning_system()
        self.assertFalse(sut.cleaning_system_on)
        self.assertTrue(sut.recharge_led_on)
        output_calls =[call(sut.CLEANING_SYSTEM_PIN, False), call(sut.RECHARGE_LED_PIN, True)]
        mock_gpio.assert_has_calls(output_calls)

    

