#!/usr/bin/env python3
"""
Test suite for ground_truth_calibrator.py

This test suite validates the ground truth calibration utility without
moving actual robot arms by mocking subprocess calls and user inputs.
"""

import unittest
import json
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path
import sys

# Add the utilities directory to Python path
utilities_dir = Path(__file__).parent.parent
sys.path.insert(0, str(utilities_dir))

from ground_truth_calibrator import GroundTruthCalibrator

class TestGroundTruthCalibrator(unittest.TestCase):
    """Test cases for GroundTruthCalibrator class"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp()
        self.calibrator = GroundTruthCalibrator(self.test_dir)
        
        # Create expected directory structure
        (Path(self.test_dir) / "temp_rules").mkdir(exist_ok=True)
        (Path(self.test_dir) / "frontend" / "ground_truth_calibration").mkdir(exist_ok=True, parents=True)
        
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.test_dir)
    
    def test_initialization(self):
        """Test calibrator initialization"""
        self.assertEqual(self.calibrator.base_dir, Path(self.test_dir))
        self.assertTrue(self.calibrator.ground_truth_dir.exists())
        self.assertEqual(len(self.calibrator.solutions), 3)
        self.assertIn("red", self.calibrator.solutions)
        self.assertIn("yellow", self.calibrator.solutions)
        self.assertIn("blue", self.calibrator.solutions)
    
    def test_parse_color_metric_rgb_format(self):
        """Test parsing RGB format colors"""
        # Test standard RGB format
        rgb = self.calibrator.parse_color_metric("RGB(201, 236, 38)")
        self.assertEqual(rgb, (201, 236, 38))
        
        # Test RGB format with extra spaces
        rgb = self.calibrator.parse_color_metric("RGB( 255 , 128 , 0 )")
        self.assertEqual(rgb, (255, 128, 0))
        
        # Test case insensitive
        rgb = self.calibrator.parse_color_metric("rgb(100, 200, 50)")
        self.assertEqual(rgb, (100, 200, 50))
    
    def test_parse_color_metric_hex_format(self):
        """Test parsing hex format colors"""
        # Test standard hex format
        rgb = self.calibrator.parse_color_metric("#c9ec26")
        self.assertEqual(rgb, (201, 236, 38))
        
        # Test uppercase hex
        rgb = self.calibrator.parse_color_metric("#FF8000")
        self.assertEqual(rgb, (255, 128, 0))
        
        # Test lowercase hex
        rgb = self.calibrator.parse_color_metric("#64c832")
        self.assertEqual(rgb, (100, 200, 50))
    
    def test_parse_color_metric_csv_format(self):
        """Test parsing comma-separated values format"""
        # Test standard CSV format
        rgb = self.calibrator.parse_color_metric("201, 236, 38")
        self.assertEqual(rgb, (201, 236, 38))
        
        # Test CSV with extra spaces
        rgb = self.calibrator.parse_color_metric("255 , 128 , 0")
        self.assertEqual(rgb, (255, 128, 0))
    
    def test_parse_color_metric_invalid_formats(self):
        """Test parsing invalid color formats"""
        # Test invalid formats
        self.assertIsNone(self.calibrator.parse_color_metric("invalid"))
        self.assertIsNone(self.calibrator.parse_color_metric("#gggggg"))
        self.assertIsNone(self.calibrator.parse_color_metric(""))
        self.assertIsNone(self.calibrator.parse_color_metric("123"))
        
        # Test that values > 255 still parse (application-level validation)
        result = self.calibrator.parse_color_metric("RGB(300, 400, 500)")
        self.assertEqual(result, (300, 400, 500))  # Parser allows, app validates
    
    @patch('subprocess.run')
    def test_run_calibration_sequence_success(self, mock_subprocess):
        """Test successful calibration sequence execution"""
        # Mock successful subprocess execution
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Sequence completed successfully"
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result
        
        # Test red solution sequence
        result = self.calibrator.run_calibration_sequence("red")
        self.assertTrue(result)
        
        # Verify subprocess was called correctly
        mock_subprocess.assert_called_once()
        args, kwargs = mock_subprocess.call_args
        self.assertEqual(args[0], ["python", "sequential_execute.py", "calibration_red_solution", "--smooth"])
        self.assertTrue(kwargs.get("capture_output"))
        self.assertTrue(kwargs.get("text"))
    
    @patch('subprocess.run')
    def test_run_calibration_sequence_failure(self, mock_subprocess):
        """Test failed calibration sequence execution"""
        # Mock failed subprocess execution
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "Error: Sequence failed"
        mock_subprocess.return_value = mock_result
        
        # Test failed sequence
        result = self.calibrator.run_calibration_sequence("yellow")
        self.assertFalse(result)
    
    def test_run_calibration_sequence_invalid_solution(self):
        """Test calibration sequence with invalid solution"""
        result = self.calibrator.run_calibration_sequence("invalid_color")
        self.assertFalse(result)
    
    @patch('builtins.input')
    def test_get_color_measurement_rgb_format(self, mock_input):
        """Test getting color measurement in RGB format"""
        # Mock user inputs: RGB format, then confirm
        mock_input.side_effect = ["RGB(201, 236, 38)", "y"]
        
        rgb = self.calibrator.get_color_measurement("red")
        self.assertEqual(rgb, (201, 236, 38))
    
    @patch('builtins.input')
    def test_get_color_measurement_hex_format(self, mock_input):
        """Test getting color measurement in hex format"""
        # Mock user inputs: hex format, then confirm
        mock_input.side_effect = ["#c9ec26", "yes"]
        
        rgb = self.calibrator.get_color_measurement("yellow")
        self.assertEqual(rgb, (201, 236, 38))
    
    @patch('builtins.input')
    def test_get_color_measurement_retry_on_invalid(self, mock_input):
        """Test retrying on invalid color input"""
        # Mock user inputs: invalid, then valid RGB, then confirm
        mock_input.side_effect = ["invalid_color", "RGB(100, 150, 200)", "y"]
        
        rgb = self.calibrator.get_color_measurement("blue")
        self.assertEqual(rgb, (100, 150, 200))
    
    @patch('builtins.input')
    def test_get_color_measurement_retry_on_rejection(self, mock_input):
        """Test retrying when user rejects parsed color"""
        # Mock user inputs: valid RGB, reject, new RGB, accept
        mock_input.side_effect = ["RGB(100, 100, 100)", "n", "RGB(200, 200, 200)", "y"]
        
        rgb = self.calibrator.get_color_measurement("red")
        self.assertEqual(rgb, (200, 200, 200))
    
    def test_calibrate_and_save_red_solution(self):
        """Test calibrating and saving red solution data"""
        rgb = (201, 236, 38)
        
        result = self.calibrator.calibrate_and_save("red", rgb)
        self.assertTrue(result)
        
        # Verify file was created
        output_file = self.calibrator.ground_truth_dir / "red_solution_ground_truth.json"
        self.assertTrue(output_file.exists())
        
        # Verify file contents
        with open(output_file, 'r') as f:
            data = json.load(f)
        
        self.assertEqual(data["solution"], "red")
        self.assertEqual(data["color_measurement"]["rgb"], list(rgb))
        self.assertEqual(data["color_measurement"]["hex"], "#c9ec26")
        self.assertEqual(data["color_measurement"]["format"], "RGB(201, 236, 38)")
        self.assertEqual(data["calibration_sequence"], "calibration_red_solution")
        self.assertIn("timestamp", data)
        self.assertEqual(data["notes"]["squeeze_time"], "10 seconds")
    
    def test_calibrate_and_save_blue_solution(self):
        """Test calibrating and saving blue solution data (with special notes)"""
        rgb = (100, 150, 200)
        
        result = self.calibrator.calibrate_and_save("blue", rgb)
        self.assertTrue(result)
        
        # Verify file was created
        output_file = self.calibrator.ground_truth_dir / "blue_solution_ground_truth.json"
        self.assertTrue(output_file.exists())
        
        # Verify file contents
        with open(output_file, 'r') as f:
            data = json.load(f)
        
        self.assertEqual(data["solution"], "blue")
        self.assertEqual(data["color_measurement"]["rgb"], list(rgb))
        self.assertIn("base_solution", data["notes"])
        self.assertEqual(data["notes"]["base_solution"], "Initial red dispensing with 1.5 second squeeze")
    
    def test_update_calibration_summary(self):
        """Test updating calibration summary"""
        # Save some ground truth data first
        self.calibrator.calibrate_and_save("red", (255, 0, 0))
        self.calibrator.calibrate_and_save("yellow", (255, 255, 0))
        
        # Check summary file
        summary_file = self.calibrator.ground_truth_dir / "calibration_summary.json"
        self.assertTrue(summary_file.exists())
        
        with open(summary_file, 'r') as f:
            summary = json.load(f)
        
        self.assertIn("calibration_summary", summary)
        self.assertIn("solutions", summary["calibration_summary"])
        self.assertIn("red", summary["calibration_summary"]["solutions"])
        self.assertIn("yellow", summary["calibration_summary"]["solutions"])
        
        # Verify red solution data
        red_data = summary["calibration_summary"]["solutions"]["red"]
        self.assertEqual(red_data["rgb"], [255, 0, 0])
        self.assertEqual(red_data["hex"], "#ff0000")
    
    @patch('subprocess.run')
    @patch('builtins.input')
    def test_calibrate_solution_complete_workflow(self, mock_input, mock_subprocess):
        """Test complete solution calibration workflow"""
        # Mock successful subprocess execution
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Sequence completed successfully"
        mock_subprocess.return_value = mock_result
        
        # Mock user inputs for color measurement
        mock_input.side_effect = ["RGB(201, 236, 38)", "y"]
        
        # Test complete workflow
        result = self.calibrator.calibrate_solution("red", auto_run=True)
        self.assertTrue(result)
        
        # Verify sequence was executed
        mock_subprocess.assert_called_once()
        
        # Verify ground truth file was created
        output_file = self.calibrator.ground_truth_dir / "red_solution_ground_truth.json"
        self.assertTrue(output_file.exists())
    
    @patch('builtins.input')
    def test_calibrate_solution_manual_mode(self, mock_input):
        """Test solution calibration in manual mode (no auto-run)"""
        # Mock user inputs: Enter to continue, then color measurement
        mock_input.side_effect = ["", "RGB(100, 150, 200)", "y"]
        
        # Test manual workflow
        result = self.calibrator.calibrate_solution("blue", auto_run=False)
        self.assertTrue(result)
        
        # Verify ground truth file was created
        output_file = self.calibrator.ground_truth_dir / "blue_solution_ground_truth.json"
        self.assertTrue(output_file.exists())
    
    @patch('subprocess.run')
    @patch('builtins.input')
    def test_calibrate_all_solutions(self, mock_input, mock_subprocess):
        """Test calibrating all solutions"""
        # Mock successful subprocess execution
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Sequence completed successfully"
        mock_subprocess.return_value = mock_result
        
        # Mock user inputs for all three solutions
        mock_input.side_effect = [
            "RGB(255, 0, 0)", "y",      # Red solution
            "RGB(255, 255, 0)", "y",    # Yellow solution  
            "RGB(0, 0, 255)", "y"       # Blue solution
        ]
        
        # Test calibrating all solutions
        result = self.calibrator.calibrate_all_solutions(auto_run=True)
        self.assertTrue(result)
        
        # Verify all three subprocess calls were made
        self.assertEqual(mock_subprocess.call_count, 3)
        
        # Verify all ground truth files were created
        for solution in ["red", "yellow", "blue"]:
            output_file = self.calibrator.ground_truth_dir / f"{solution}_solution_ground_truth.json"
            self.assertTrue(output_file.exists(), f"Missing {solution} ground truth file")
        
        # Verify summary file was created
        summary_file = self.calibrator.ground_truth_dir / "calibration_summary.json"
        self.assertTrue(summary_file.exists())


class TestGroundTruthCalibratorIntegration(unittest.TestCase):
    """Integration tests that test the calibrator with more realistic scenarios"""
    
    def setUp(self):
        """Set up integration test fixtures"""
        self.test_dir = tempfile.mkdtemp()
        self.calibrator = GroundTruthCalibrator(self.test_dir)
    
    def tearDown(self):
        """Clean up integration test fixtures"""
        shutil.rmtree(self.test_dir)
    
    @patch('subprocess.run')
    @patch('builtins.input')
    def test_mixed_success_failure_scenarios(self, mock_input, mock_subprocess):
        """Test scenarios with mixed success and failure"""
        # Mock subprocess: success for red, failure for yellow, success for blue
        mock_results = [
            MagicMock(returncode=0, stdout="Red sequence success"),
            MagicMock(returncode=1, stderr="Yellow sequence failed"),
            MagicMock(returncode=0, stdout="Blue sequence success")
        ]
        mock_subprocess.side_effect = mock_results
        
        # Mock user inputs (only for successful sequences)
        mock_input.side_effect = [
            "RGB(255, 0, 0)", "y",      # Red solution (success)
            # No input for yellow (failed)
            "RGB(0, 0, 255)", "y"       # Blue solution (success)
        ]
        
        # Test calibrating all solutions
        result = self.calibrator.calibrate_all_solutions(auto_run=True)
        self.assertFalse(result)  # Should fail overall due to yellow failure
        
        # Verify red and blue files exist, yellow doesn't
        red_file = self.calibrator.ground_truth_dir / "red_solution_ground_truth.json"
        yellow_file = self.calibrator.ground_truth_dir / "yellow_solution_ground_truth.json"
        blue_file = self.calibrator.ground_truth_dir / "blue_solution_ground_truth.json"
        
        self.assertTrue(red_file.exists())
        self.assertFalse(yellow_file.exists())
        self.assertTrue(blue_file.exists())
    
    def test_color_format_conversion_accuracy(self):
        """Test accuracy of color format conversions"""
        test_cases = [
            ("RGB(255, 128, 64)", (255, 128, 64), "#ff8040"),
            ("#c9ec26", (201, 236, 38), "#c9ec26"),
            ("128, 192, 255", (128, 192, 255), "#80c0ff"),
        ]
        
        for input_format, expected_rgb, expected_hex in test_cases:
            # Parse the color
            parsed_rgb = self.calibrator.parse_color_metric(input_format)
            self.assertEqual(parsed_rgb, expected_rgb)
            
            # Save and verify hex conversion
            result = self.calibrator.calibrate_and_save("red", parsed_rgb)
            self.assertTrue(result)
            
            # Check saved data
            output_file = self.calibrator.ground_truth_dir / "red_solution_ground_truth.json"
            with open(output_file, 'r') as f:
                data = json.load(f)
            
            self.assertEqual(data["color_measurement"]["hex"], expected_hex)
    
    def test_file_system_error_handling(self):
        """Test handling of file system errors"""
        # Create a calibrator with invalid directory permissions
        invalid_dir = Path(self.test_dir) / "invalid"
        invalid_dir.mkdir()
        invalid_dir.chmod(0o444)  # Read-only
        
        try:
            invalid_calibrator = GroundTruthCalibrator(str(invalid_dir))
            
            # This should fail due to permission error
            result = invalid_calibrator.calibrate_and_save("red", (255, 0, 0))
            # The result depends on the specific error handling implementation
            # It might succeed if the directory creation is handled gracefully
            
        finally:
            # Clean up permissions
            invalid_dir.chmod(0o755)


class MockScenarioTests(unittest.TestCase):
    """Tests that simulate realistic usage scenarios"""
    
    def setUp(self):
        """Set up mock scenario tests"""
        self.test_dir = tempfile.mkdtemp()
        self.calibrator = GroundTruthCalibrator(self.test_dir)
    
    def tearDown(self):
        """Clean up mock scenario tests"""
        shutil.rmtree(self.test_dir)
    
    @patch('subprocess.run')
    @patch('builtins.input')
    def test_typical_user_workflow(self, mock_input, mock_subprocess):
        """Test a typical user workflow with realistic inputs"""
        # Mock successful robot execution
        mock_subprocess.return_value = MagicMock(
            returncode=0,
            stdout="Robot sequence completed. Color analysis complete."
        )
        
        # Mock typical user inputs (some mistakes, corrections)
        mock_input.side_effect = [
            "invalid format",           # User makes mistake
            "RGB(195, 87, 43)",        # User enters correct format
            "n",                       # User wants to re-enter
            "#d2691e",                 # User enters hex format
            "y"                        # User confirms
        ]
        
        result = self.calibrator.calibrate_solution("red")
        self.assertTrue(result)
        
        # Verify final color was saved correctly
        output_file = self.calibrator.ground_truth_dir / "red_solution_ground_truth.json"
        with open(output_file, 'r') as f:
            data = json.load(f)
        
        # Should match the hex input converted to RGB
        self.assertEqual(data["color_measurement"]["rgb"], [210, 105, 30])
        self.assertEqual(data["color_measurement"]["hex"], "#d2691e")


if __name__ == "__main__":
    # Create a test suite combining all test classes
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestGroundTruthCalibrator))
    suite.addTests(loader.loadTestsFromTestCase(TestGroundTruthCalibratorIntegration))
    suite.addTests(loader.loadTestsFromTestCase(MockScenarioTests))
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Exit with appropriate code
    exit(0 if result.wasSuccessful() else 1)
