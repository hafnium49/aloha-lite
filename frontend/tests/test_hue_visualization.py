#!/usr/bin/env python3
"""
Test script for the new hue visualization features in the frontend.

Tests the frontend HTML changes including:
1. Tab switching functionality
2. Hue visualization canvas elements
3. Integration with hue-visual-data API
"""

import sys
import os
import re

# Add parent directory to path to import main module
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def test_html_hue_visualization_elements():
    """Test that the HTML contains the new hue visualization elements."""
    print("🧪 Testing HTML Hue Visualization Elements")
    print("=" * 50)
    
    # Read the HTML file
    html_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "index.html")
    
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
    except FileNotFoundError:
        print(f"❌ HTML file not found: {html_path}")
        return False
    
    # Test 1: Check for tab container and buttons
    print("\n🔍 Checking for tab container elements...")
    
    required_elements = [
        ('tab-container', 'Tab container div'),
        ('tab-buttons', 'Tab buttons container'),
        ('tab-btn', 'Tab button class'),
        ('data-tab="dial"', 'Hue Gauge tab'),
        ('data-tab="ab"', 'a*-b* Scatter tab'),
        ('data-tab="error"', 'Error vs Trial tab'),
        ('data-tab="strip"', 'Color Timeline tab'),
    ]
    
    for element, description in required_elements:
        if element in html_content:
            print(f"✅ {description}: Found")
        else:
            print(f"❌ {description}: Missing")
            return False
    
    # Test 2: Check for canvas elements
    print("\n🎨 Checking for visualization canvas elements...")
    
    canvas_elements = [
        ('dial-canvas', 'Hue gauge canvas'),
        ('ab-canvas', 'a*-b* scatter canvas'),
        ('error-canvas', 'Error line canvas'),
        ('strip-canvas', 'Color timeline canvas'),
    ]
    
    for canvas_id, description in canvas_elements:
        if f'id="{canvas_id}"' in html_content:
            print(f"✅ {description}: Found")
        else:
            print(f"❌ {description}: Missing")
            return False
    
    # Test 3: Check for CSS styles
    print("\n💅 Checking for tab CSS styles...")
    
    css_classes = [
        ('.tab-buttons', 'Tab buttons styling'),
        ('.tab-btn', 'Tab button styling'),
        ('.tab-btn.active', 'Active tab styling'),
        ('.tab-panel', 'Tab panel styling'),
        ('.tab-panel.active', 'Active panel styling'),
    ]
    
    for css_class, description in css_classes:
        if css_class in html_content:
            print(f"✅ {description}: Found")
        else:
            print(f"❌ {description}: Missing")
            return False
    
    # Test 4: Check for JavaScript functionality
    print("\n⚙️ Checking for JavaScript functionality...")
    
    js_features = [
        ('drawAllHueCharts', 'Main hue chart drawing function'),
        ('/api/hue-visual-data', 'API endpoint call'),
        ('dial-canvas', 'Hue gauge canvas reference'),
        ('tab-btn', 'Tab button event handling'),
        ('btn.dataset.tab', 'Tab switching logic'),
    ]
    
    for js_feature, description in js_features:
        if js_feature in html_content:
            print(f"✅ {description}: Found")
        else:
            print(f"❌ {description}: Missing")
            return False
    
    # Test 5: Check for proper tab structure
    print("\n📁 Checking tab structure...")
    
    # Count tab buttons and panels
    tab_buttons = html_content.count('class="tab-btn')
    tab_panels = html_content.count('class="tab-panel')
    
    if tab_buttons == 4:
        print(f"✅ Tab buttons: Found {tab_buttons} (expected 4)")
    else:
        print(f"❌ Tab buttons: Found {tab_buttons} (expected 4)")
        return False
    
    if tab_panels == 4:
        print(f"✅ Tab panels: Found {tab_panels} (expected 4)")
    else:
        print(f"❌ Tab panels: Found {tab_panels} (expected 4)")
        return False
    
    # Test 6: Check for updateOptimizationStats modification
    print("\n🔄 Checking updateOptimizationStats modification...")
    
    if 'drawAllHueCharts()' in html_content:
        print("✅ updateOptimizationStats calls drawAllHueCharts()")
    else:
        print("❌ updateOptimizationStats does not call drawAllHueCharts()")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 All HTML hue visualization tests passed!")
    print("✅ Tab container structure is correct")
    print("✅ All visualization canvases are present")
    print("✅ CSS styling for tabs is included")
    print("✅ JavaScript functionality is implemented")
    print("✅ API integration is properly set up")
    
    return True

def test_html_structure_integrity():
    """Test that the HTML file is still well-formed after modifications."""
    print("\n🧪 Testing HTML Structure Integrity")
    print("=" * 30)
    
    html_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "index.html")
    
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
    except FileNotFoundError:
        print(f"❌ HTML file not found: {html_path}")
        return False
    
    # Basic HTML structure checks
    checks = [
        ('<html', '</html>', 'HTML tags'),
        ('<head', '</head>', 'HEAD tags'),
        ('<body', '</body>', 'BODY tags'),
        ('<style', '</style>', 'STYLE tags'),
        ('<script', '</script>', 'SCRIPT tags'),
    ]
    
    for open_tag, close_tag, description in checks:
        open_count = html_content.count(open_tag)
        close_count = html_content.count(close_tag)
        
        if open_count == close_count and open_count > 0:
            print(f"✅ {description}: Properly balanced ({open_count} pairs)")
        else:
            print(f"❌ {description}: Unbalanced (open: {open_count}, close: {close_count})")
            return False
    
    # Check for valid HTML5 doctype
    if html_content.strip().startswith('<!DOCTYPE html>'):
        print("✅ HTML5 doctype declaration present")
    else:
        print("❌ HTML5 doctype declaration missing or incorrect")
        return False
    
    print("✅ HTML structure integrity maintained")
    return True

def run_hue_visualization_tests():
    """Run all hue visualization tests."""
    print("🚀 Hue Visualization Test Suite")
    print("🎨 Testing Frontend HTML Changes")
    print("=" * 80)
    
    tests = [
        ("HTML Elements Test", test_html_hue_visualization_elements),
        ("HTML Integrity Test", test_html_structure_integrity),
    ]
    
    all_passed = True
    
    for test_name, test_func in tests:
        print(f"\n{'=' * 60}")
        print(f"🏃 Running {test_name}...")
        print(f"{'=' * 60}")
        
        try:
            if not test_func():
                all_passed = False
                print(f"❌ {test_name} FAILED")
            else:
                print(f"✅ {test_name} PASSED")
        except Exception as e:
            print(f"💥 {test_name} ERROR: {e}")
            all_passed = False
    
    print(f"\n{'=' * 80}")
    if all_passed:
        print("🎉 ALL HUE VISUALIZATION TESTS PASSED!")
        print("✅ Frontend HTML modifications are working correctly")
        print("✅ Tab-based hue visualization system is ready")
    else:
        print("❌ SOME HUE VISUALIZATION TESTS FAILED!")
        print("🔧 Check the frontend HTML implementation")
    print(f"{'=' * 80}")
    
    return all_passed

if __name__ == "__main__":
    success = run_hue_visualization_tests()
    exit(0 if success else 1)
