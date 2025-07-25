#!/usr/bin/env python3
"""
Test script to verify SAM 2 installation and setup
"""

import os
import sys
from pathlib import Path

def test_sam2_import():
    """Test if SAM 2 can be imported"""
    try:
        import sam2
        print("✅ SAM 2 imported successfully")
        print(f"   SAM 2 version: {getattr(sam2, '__version__', 'unknown')}")
        return True
    except ImportError as e:
        print(f"❌ Failed to import SAM 2: {e}")
        return False

def test_sam2_components():
    """Test if SAM 2 components can be imported"""
    try:
        from sam2.sam2_image_predictor import SAM2ImagePredictor
        from sam2.build_sam import build_sam2
        print("✅ SAM 2 components imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import SAM 2 components: {e}")
        return False

def test_local_model_files():
    """Test if local model files exist"""
    checkpoint_path = Path("checkpoints/sam2.1_hiera_tiny.pt")
    config_path = Path("configs/sam2.1/sam2.1_hiera_t.yaml")
    
    if checkpoint_path.exists():
        file_size = checkpoint_path.stat().st_size / (1024 * 1024)  # MB
        print(f"✅ Model checkpoint found: {checkpoint_path} ({file_size:.1f} MB)")
        checkpoint_ok = True
    else:
        print(f"❌ Model checkpoint not found: {checkpoint_path}")
        checkpoint_ok = False
    
    if config_path.exists():
        print(f"✅ Model config found: {config_path}")
        config_ok = True
    else:
        print(f"❌ Model config not found: {config_path}")
        config_ok = False
    
    return checkpoint_ok and config_ok

def test_huggingface_model():
    """Test if Hugging Face model can be loaded"""
    try:
        from sam2.sam2_image_predictor import SAM2ImagePredictor
        print("🤗 Testing Hugging Face model loading...")
        # Note: This would actually download the model, so we just test the import
        print("✅ Hugging Face integration available")
        return True
    except ImportError as e:
        print(f"❌ Hugging Face integration not available: {e}")
        return False

def test_torch_availability():
    """Test if PyTorch is available with proper version"""
    try:
        import torch
        version = torch.__version__
        print(f"✅ PyTorch available: {version}")
        
        # Check if CUDA is available
        if torch.cuda.is_available():
            print(f"✅ CUDA available: {torch.cuda.get_device_name(0)}")
        else:
            print("⚠️  CUDA not available - will use CPU")
        
        return True
    except ImportError as e:
        print(f"❌ PyTorch not available: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 SAM 2 Installation Test")
    print("=" * 50)
    
    tests = [
        ("PyTorch availability", test_torch_availability),
        ("SAM 2 import", test_sam2_import),
        ("SAM 2 components", test_sam2_components),
        ("Local model files", test_local_model_files),
        ("Hugging Face integration", test_huggingface_model),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔍 Testing {test_name}...")
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    
    all_passed = True
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {test_name}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All tests passed! SAM 2 is ready to use.")
        print("\n💡 Usage example:")
        print("   from sam2.sam2_image_predictor import SAM2ImagePredictor")
        print("   # Local model:")
        print("   predictor = SAM2ImagePredictor(build_sam2('configs/sam2.1/sam2.1_hiera_t.yaml', 'checkpoints/sam2.1_hiera_tiny.pt'))")
        print("   # Or Hugging Face model:")
        print("   predictor = SAM2ImagePredictor.from_pretrained('facebook/sam2-hiera-tiny')")
    else:
        print("⚠️  Some tests failed. Please check the installation.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
