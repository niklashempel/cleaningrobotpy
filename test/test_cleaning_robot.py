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

    @patch.object(CleaningRobot, 'activate_wheel_motor')
    @patch.object(IBS, 'get_charge_left')
    def test_execute_command_move(self, mock_get_charge_left: Mock, mock_activate_wheel_motor: Mock):
        mock_get_charge_left.return_value = 100
        sut = CleaningRobot()
        sut.initialize_robot()

        status = sut.execute_command(sut.FORWARD)
        self.assertEqual(0, sut.pos_x)
        self.assertEqual(1, sut.pos_y)
        self.assertEqual(sut.N, sut.heading)
        self.assertEqual("(0,1,N)", status)

        mock_activate_wheel_motor.assert_called_once()

    @patch.object(CleaningRobot, 'activate_rotation_motor')
    @patch.object(IBS, 'get_charge_left')
    def test_execute_command_turn_left(self, mock_get_charge_left: Mock, mock_activate_rotation_motor: Mock):
        mock_get_charge_left.return_value = 100
        sut = CleaningRobot()
        sut.initialize_robot()

        status = sut.execute_command(sut.LEFT)
        self.assertEqual(0, sut.pos_x)
        self.assertEqual(0, sut.pos_y)
        self.assertEqual(sut.W, sut.heading)
        self.assertEqual("(0,0,W)", status)

        mock_activate_rotation_motor.assert_called_once_with(sut.LEFT)

    @patch.object(CleaningRobot, 'activate_rotation_motor')
    @patch.object(IBS, 'get_charge_left')
    def test_execute_command_turn_right(self, mock_get_charge_left: Mock, mock_activate_rotation_motor: Mock):
        mock_get_charge_left.return_value = 100
        sut = CleaningRobot()
        sut.initialize_robot()

        status = sut.execute_command(sut.RIGHT)
        self.assertEqual(0, sut.pos_x)
        self.assertEqual(0, sut.pos_y)
        self.assertEqual(sut.E, sut.heading)
        self.assertEqual("(0,0,E)", status)
        mock_activate_rotation_motor.assert_called_once_with(sut.RIGHT)

    @patch.object(GPIO, "input")
    def test_obstacle_found_positive(self, mock_infrared_sensor: Mock):
        sut = CleaningRobot()
        mock_infrared_sensor.return_value = True
        self.assertTrue(sut.obstacle_found())

    
    @patch.object(GPIO, "input")
    def test_obstacle_found_negative(self, mock_infrared_sensor: Mock):
        sut = CleaningRobot()
        mock_infrared_sensor.return_value = False
        self.assertFalse(sut.obstacle_found())

    
    @patch.object(CleaningRobot, 'activate_wheel_motor')
    @patch.object(CleaningRobot, "obstacle_found")
    @patch.object(IBS, 'get_charge_left')
    def test_execute_command_move_when_obstacle_found(self, mock_get_charge_left: Mock, mock_obstacle_found: Mock, mock_activate_wheel_motor: Mock):
        mock_get_charge_left.return_value = 100
        mock_obstacle_found.return_value = True        
        sut = CleaningRobot()
        sut.initialize_robot()

        status = sut.execute_command(sut.FORWARD)
        self.assertEqual(0, sut.pos_x)
        self.assertEqual(0, sut.pos_y)
        self.assertEqual(sut.N, sut.heading)
        self.assertEqual("(0,0,N)(0,1)", status)
        mock_activate_wheel_motor.assert_not_called()

    @patch.object(IBS, 'get_charge_left')
    @patch.object(GPIO, 'output')
    def test_execute_command_when_not_enough_charge(self, mock_gpio: Mock, mock_get_charge_left: Mock):
        mock_get_charge_left.return_value = 10
        sut = CleaningRobot()
        sut.initialize_robot()
        status = sut.execute_command(sut.FORWARD)

        calls = [call(sut.CLEANING_SYSTEM_PIN, False), call(sut.RECHARGE_LED_PIN, True)]
        mock_gpio.assert_has_calls(calls)
        self.assertFalse(sut.cleaning_system_on)
        self.assertTrue(sut.recharge_led_on)
        self.assertEqual("!(0,0,N)", status)

    @patch.object(GPIO, "input")
    def test_enough_water(self, mock_water_sensor: Mock):
        mock_water_sensor.return_value = True
        sut = CleaningRobot()
        self.assertTrue(sut.enough_water())

    @patch.object(GPIO, "input")
    def test_not_enough_water(self, mock_water_sensor: Mock):
        mock_water_sensor.return_value = False
        sut = CleaningRobot()
        self.assertFalse(sut.enough_water())

    @patch.object(CleaningRobot, 'enough_water')
    @patch.object(IBS, 'get_charge_left')
    def test_execute_command_not_enough_water(self, mock_get_charge_left: Mock, mock_enough_water: Mock):
        mock_enough_water.return_value = False
        mock_get_charge_left.return_value = 100
        sut = CleaningRobot()
        sut.initialize_robot()
        status = sut.execute_command(sut.FORWARD)
        self.assertEqual("?(0,1,N)", status)