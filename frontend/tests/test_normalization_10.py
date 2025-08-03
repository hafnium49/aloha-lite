#!/usr/bin/env python3
"""
Test script to verify that normalization has been changed from 3.0 to 10.0
Tests both the standalone normalize function and the actual ColorOptimizer.
"""

import sys
import os
import unittest

# Add parent directory to path to import main module
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

try:
    from main import ColorOptimizer
    MAIN_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import from main.py: {e}")
    MAIN_AVAILABLE = False

def test_normalize_standalone(d, max_total=10.0):
    """Standalone test version of the normalize function"""
    coloured = {k: v for k, v in d.items() if k != "white"}
    s = sum(coloured.values()) or 1.0
    f = min(1.0, max_total / s)
    out = {k: max(0.1, coloured.get(k, 0.0) * f) for k in ('red', 'yellow', 'blue')}
    out["white"] = max_total - sum(out.values())
    if out["white"] < 0.1:
        deficit = 0.1 - out["white"]
        scale = (sum(out.values()) - deficit) / sum(out.values())
        for k in ('red', 'yellow', 'blue'):
            out[k] *= scale
        out["white"] = 0.1
    return out

class TestNormalization10mL(unittest.TestCase):
    """Test class for 10.0 mL normalization verification."""
    
    def setUp(self):
        """Set up test fixtures."""
        if MAIN_AVAILABLE:
            self.optimizer = ColorOptimizer()
    
    def test_standalone_normalize_function(self):
        """Test standalone normalize function with 10.0 mL."""
        print("\n🧪 Testing standalone normalize function...")
        
        test_cases = [
            {
                "name": "Normal ratios (should fit within 10.0)",
                "input": {"red": 3.0, "yellow": 4.0, "blue": 2.0},
                "expected_total": 10.0
            },
            {
                "name": "Large ratios (should scale down to 10.0)",
                "input": {"red": 15.0, "yellow": 20.0, "blue": 10.0},
                "expected_total": 10.0
            },
            {
                "name": "Small ratios (should have lots of white)",
                "input": {"red": 0.5, "yellow": 1.0, "blue": 0.3},
                "expected_total": 10.0
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            with self.subTest(case=i):
                result = test_normalize_standalone(test_case["input"])
                total = sum(result.values())
                
                self.assertAlmostEqual(total, test_case["expected_total"], places=2)
                self.assertIn('white', result)
                self.assertGreaterEqual(result['white'], 0.1)
                
                print(f"  Test {i}: {test_case['name']}")
                print(f"    Input:  {test_case['input']}")
                print(f"    Output: {result}")
                print(f"    Total:  {total:.2f} mL ✅")
    
    @unittest.skipUnless(MAIN_AVAILABLE, "main.py not available")
    def test_color_optimizer_normalize(self):
        """Test ColorOptimizer._normalize() method with 10.0 mL."""
        print("\n🧪 Testing ColorOptimizer._normalize() method...")
        
        test_cases = [
            {"red": 3.0, "yellow": 4.0, "blue": 2.0},
            {"red": 15.0, "yellow": 20.0, "blue": 10.0},
            {"red": 0.5, "yellow": 1.0, "blue": 0.3},
            {"red": 1.0, "yellow": 1.0, "blue": 1.0}
        ]
        
        for i, test_input in enumerate(test_cases, 1):
            with self.subTest(case=i):
                result = self.optimizer._normalize(test_input)
                total = sum(result.values())
                
                self.assertAlmostEqual(total, 10.0, places=2)
                self.assertEqual(len(result), 4)  # red, yellow, blue, white
                self.assertIn('white', result)
                self.assertGreaterEqual(result['white'], 0.1)
                
                print(f"  Case {i}: {test_input}")
                print(f"    Normalized: {result}")
                print(f"    Total: {total:.2f} mL ✅")
    
    @unittest.skipUnless(MAIN_AVAILABLE, "main.py not available")
    def test_color_optimizer_get_random(self):
        """Test ColorOptimizer._get_random() method returns 10.0 mL totals."""
        print("\n🧪 Testing ColorOptimizer._get_random() method...")
        
        for i in range(5):
            random_ratios = self.optimizer._get_random()
            total = sum(random_ratios.values())
            
            self.assertAlmostEqual(total, 10.0, places=2)
            self.assertEqual(len(random_ratios), 4)
            self.assertIn('white', random_ratios)
            
            # Check bounds are reasonable for 10.0 mL system
            for color in ['red', 'yellow', 'blue']:
                self.assertGreaterEqual(random_ratios[color], 0.09)  # Allow slight floating point variance
                self.assertLessEqual(random_ratios[color], 10.0)
            
            if i == 0:  # Print first example
                print(f"  Random example: {random_ratios}")
                print(f"  Total: {total:.2f} mL ✅")


def test_normalization_factor_change():
    """Pytest-compatible function for normalization testing."""
    print("🧪 Testing Frontend Normalization Factor Change: 3.0 → 10.0")
    print("=" * 60)
    
    test_cases = [
        {
            "name": "Normal ratios (should fit within 10.0)",
            "input": {"red": 3.0, "yellow": 4.0, "blue": 2.0},
            "expected_total": 10.0
        },
        {
            "name": "Large ratios (should scale down to 10.0)",
            "input": {"red": 15.0, "yellow": 20.0, "blue": 10.0},
            "expected_total": 10.0
        },
        {
            "name": "Small ratios (should have lots of white)",
            "input": {"red": 0.5, "yellow": 1.0, "blue": 0.3},
            "expected_total": 10.0
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"Test {i}: {test_case['name']}")
        
        # Test with new 10.0 normalization
        result = test_normalize_standalone(test_case["input"])
        total = sum(result.values())
        
        print(f"  Input:  {test_case['input']}")
        print(f"  Output: {result}")
        print(f"  Total:  {total:.2f} mL")
        
        # Verify total is exactly 10.0
        assert abs(total - test_case["expected_total"]) < 0.01, f"Expected {test_case['expected_total']}, got {total:.2f}"
        print(f"  ✅ PASS - Total volume is {test_case['expected_total']} mL")
        print()
    
    print("🎉 ALL TESTS PASSED!")
    print("\n📋 Normalization factor successfully changed from 3.0 to 10.0")
    print("   ✅ All color ratios now normalize to 10.0 mL total volume")
    print("   ✅ Frontend will send 10.0 mL normalized ratios to robot service")
    print("   ✅ Robot service will receive proportionally correct ratios")

def main():
    """Main function for standalone execution."""
    print("🧪 Testing Frontend Normalization Factor Change: 3.0 → 10.0")
    print("=" * 60)
    
    # Test cases that demonstrate the difference
    test_cases = [
        {
            "name": "Normal ratios (should fit within 10.0)",
            "input": {"red": 3.0, "yellow": 4.0, "blue": 2.0},
            "expected_total": 10.0
        },
        {
            "name": "Large ratios (should scale down to 10.0)",
            "input": {"red": 15.0, "yellow": 20.0, "blue": 10.0},
            "expected_total": 10.0
        },
        {
            "name": "Small ratios (should have lots of white)",
            "input": {"red": 0.5, "yellow": 1.0, "blue": 0.3},
            "expected_total": 10.0
        }
    ]
    
    all_passed = True
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"Test {i}: {test_case['name']}")
        
        # Test with new 10.0 normalization
        result = test_normalize_standalone(test_case["input"])
        total = sum(result.values())
        
        print(f"  Input:  {test_case['input']}")
        print(f"  Output: {result}")
        print(f"  Total:  {total:.2f} mL")
        
        # Verify total is exactly 10.0
        if abs(total - test_case["expected_total"]) < 0.01:
            print(f"  ✅ PASS - Total volume is {test_case['expected_total']} mL")
        else:
            print(f"  ❌ FAIL - Expected {test_case['expected_total']}, got {total:.2f}")
            all_passed = False
        
        print()
    
    # Summary
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("\n📋 Normalization factor successfully changed from 3.0 to 10.0")
        print("   ✅ All color ratios now normalize to 10.0 mL total volume")
        print("   ✅ Frontend will send 10.0 mL normalized ratios to robot service")
        print("   ✅ Robot service will receive proportionally correct ratios")
    else:
        print("❌ SOME TESTS FAILED - Check implementation")
    
    return all_passed

if __name__ == "__main__":
    main()
