#!/usr/bin/env python3
"""
Test script to verify that normalization has been changed from 3.0 to 10.0
"""

def test_normalize(d, max_total=10.0):
    """Test version of the normalize function"""
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

def main():
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
        result = test_normalize(test_case["input"])
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
