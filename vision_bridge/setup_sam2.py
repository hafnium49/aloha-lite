#!/usr/bin/env python3
"""
SAM 2 Setup Script
Prepares SAM 2 checkpoint and configuration files for the vision_bridge integration.

Based on Meta's official SAM 2 repository:
https://github.com/facebookresearch/sam2

This script will:
1. Clone the SAM 2 repository (if needed)
2. Download SAM 2.1 model checkpoints
3. Set up configuration files
4. Test the installation
5. Configure environment variables for vision_bridge
"""

import os
import sys
import subprocess
import urllib.request
import hashlib
from pathlib import Path
import tempfile
import shutil

# SAM 2.1 Model Information
SAM2_MODELS = {
    'tiny': {
        'checkpoint': 'sam2.1_hiera_tiny.pt',
        'config': 'configs/sam2.1/sam2.1_hiera_t.yaml',
        'url': 'https://dl.fbaipublicfiles.com/segment_anything_2/092824/sam2.1_hiera_tiny.pt',
        'size_mb': 155,
        'description': 'Fastest model, good for real-time applications'
    },
    'small': {
        'checkpoint': 'sam2.1_hiera_small.pt', 
        'config': 'configs/sam2.1/sam2.1_hiera_s.yaml',
        'url': 'https://dl.fbaipublicfiles.com/segment_anything_2/092824/sam2.1_hiera_small.pt',
        'size_mb': 185,
        'description': 'Balanced speed and accuracy'
    },
    'base_plus': {
        'checkpoint': 'sam2.1_hiera_base_plus.pt',
        'config': 'configs/sam2.1/sam2.1_hiera_b+.yaml', 
        'url': 'https://dl.fbaipublicfiles.com/segment_anything_2/092824/sam2.1_hiera_base_plus.pt',
        'size_mb': 323,
        'description': 'Good accuracy with reasonable speed'
    },
    'large': {
        'checkpoint': 'sam2.1_hiera_large.pt',
        'config': 'configs/sam2.1/sam2.1_hiera_l.yaml',
        'url': 'https://dl.fbaipublicfiles.com/segment_anything_2/092824/sam2.1_hiera_large.pt', 
        'size_mb': 898,
        'description': 'Best accuracy, slower inference'
    }
}

def print_header():
    """Print script header with information."""
    print("=" * 70)
    print("🤖 SAM 2 Setup Script for Vision Bridge Integration")
    print("=" * 70)
    print("This script prepares SAM 2.1 models for enhanced beaker detection.")
    print("Based on Meta's official SAM 2 repository.")
    print()

def check_requirements():
    """Check if required tools are available."""
    print("🔍 Checking requirements...")
    
    # Check Python version
    if sys.version_info < (3, 10):
        print("❌ Python 3.10+ required. Current version:", sys.version)
        return False
    print("✅ Python version:", sys.version.split()[0])
    
    # Check git
    try:
        subprocess.run(['git', '--version'], capture_output=True, check=True)
        print("✅ Git is available")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Git is required but not found")
        return False
    
    # Check internet connectivity
    try:
        urllib.request.urlopen('https://github.com', timeout=10)
        print("✅ Internet connectivity OK")
    except:
        print("❌ Internet connection required")
        return False
        
    return True

def setup_sam2_repository(base_dir):
    """Clone or update the SAM 2 repository."""
    sam2_repo_dir = base_dir / "sam2_repo"
    
    print(f"\n📂 Setting up SAM 2 repository in {sam2_repo_dir}...")
    
    if sam2_repo_dir.exists():
        print(f"Repository already exists at {sam2_repo_dir}")
        print("Updating repository...")
        try:
            subprocess.run(['git', 'pull'], cwd=sam2_repo_dir, check=True, capture_output=True)
            print("✅ Repository updated")
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Could not update repository: {e}")
            print("Continuing with existing repository...")
    else:
        print("Cloning SAM 2 repository...")
        try:
            subprocess.run([
                'git', 'clone', 
                'https://github.com/facebookresearch/sam2.git',
                str(sam2_repo_dir)
            ], check=True, capture_output=True)
            print("✅ Repository cloned successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to clone repository: {e}")
            return False
    
    return sam2_repo_dir

def download_checkpoint(model_info, checkpoint_dir):
    """Download a model checkpoint with progress indication."""
    checkpoint_path = checkpoint_dir / model_info['checkpoint']
    
    if checkpoint_path.exists():
        print(f"✅ Checkpoint already exists: {checkpoint_path}")
        return checkpoint_path
    
    print(f"📥 Downloading {model_info['checkpoint']} ({model_info['size_mb']}MB)...")
    
    def progress_hook(block_num, block_size, total_size):
        downloaded = block_num * block_size
        if total_size > 0:
            percent = min(100, (downloaded * 100) // total_size)
            print(f"\r   Progress: {percent}% ({downloaded // (1024*1024)}MB / {total_size // (1024*1024)}MB)", end='')
    
    try:
        urllib.request.urlretrieve(
            model_info['url'], 
            str(checkpoint_path),
            reporthook=progress_hook
        )
        print(f"\n✅ Downloaded: {checkpoint_path}")
        return checkpoint_path
    except Exception as e:
        print(f"\n❌ Download failed: {e}")
        if checkpoint_path.exists():
            checkpoint_path.unlink()
        return None

def setup_model(model_name, sam2_repo_dir, base_dir):
    """Set up a specific SAM 2 model."""
    if model_name not in SAM2_MODELS:
        print(f"❌ Unknown model: {model_name}")
        return False
    
    model_info = SAM2_MODELS[model_name]
    print(f"\n🤖 Setting up SAM 2.1 {model_name} model...")
    print(f"   Description: {model_info['description']}")
    
    # Create checkpoint directory
    checkpoint_dir = base_dir / "checkpoints"
    checkpoint_dir.mkdir(exist_ok=True)
    
    # Download checkpoint
    checkpoint_path = download_checkpoint(model_info, checkpoint_dir)
    if not checkpoint_path:
        return False
    
    # Verify config file exists in repository
    config_path = sam2_repo_dir / model_info['config']
    if not config_path.exists():
        print(f"❌ Config file not found: {config_path}")
        return False
    
    print(f"✅ Config file available: {config_path}")
    
    return {
        'checkpoint_path': checkpoint_path,
        'config_path': config_path,
        'model_info': model_info
    }

def test_sam2_installation(sam2_repo_dir, model_setup):
    """Test SAM 2 installation with a simple import test."""
    print(f"\n🧪 Testing SAM 2 installation...")
    
    # Add sam2 repository to Python path for testing
    original_path = sys.path.copy()
    sys.path.insert(0, str(sam2_repo_dir))
    
    try:
        # Test imports
        print("   Testing imports...")
        from sam2.build_sam import build_sam2
        from sam2.sam2_image_predictor import SAM2ImagePredictor
        print("   ✅ SAM 2 imports successful")
        
        # Test model loading
        print("   Testing model loading...")
        import torch
        
        # Build model
        model = build_sam2(
            str(model_setup['config_path']), 
            str(model_setup['checkpoint_path'])
        )
        
        # Create predictor
        device = "cuda" if torch.cuda.is_available() else "cpu"
        model.to(device)
        predictor = SAM2ImagePredictor(model)
        
        print(f"   ✅ Model loaded successfully on {device}")
        print("   ✅ SAM 2 installation test passed")
        
        return True
        
    except Exception as e:
        print(f"   ❌ SAM 2 test failed: {e}")
        return False
    finally:
        # Restore original Python path
        sys.path = original_path

def create_environment_script(base_dir, model_setup, sam2_repo_dir):
    """Create environment setup script for vision_bridge."""
    script_path = base_dir / "setup_sam2_environment.sh"
    
    print(f"\n📝 Creating environment setup script: {script_path}")
    
    script_content = f"""#!/bin/bash
# SAM 2 Environment Setup Script
# Generated by SAM 2 setup script

# SAM 2 Model Checkpoint and Configuration
export SAM_CHECKPOINT="{model_setup['checkpoint_path'].absolute()}"
export SAM_CONFIG="{model_setup['config_path'].absolute()}"

# Add SAM 2 repository to Python path
export PYTHONPATH="{sam2_repo_dir.absolute()}:$PYTHONPATH"

echo "🤖 SAM 2 environment configured:"
echo "   Checkpoint: $SAM_CHECKPOINT"
echo "   Config: $SAM_CONFIG"
echo "   Repository: {sam2_repo_dir.absolute()}"

# Test the environment
python3 -c "
try:
    import sys
    sys.path.insert(0, '{sam2_repo_dir.absolute()}')
    from sam2.build_sam import build_sam2
    from sam2.sam2_image_predictor import SAM2ImagePredictor
    print('✅ SAM 2 environment ready!')
except Exception as e:
    print(f'❌ Environment test failed: {{e}}')
"
"""
    
    with open(script_path, 'w') as f:
        f.write(script_content)
    
    # Make script executable
    script_path.chmod(0o755)
    
    print(f"✅ Environment script created: {script_path}")
    return script_path

def create_test_script(base_dir, sam2_repo_dir):
    """Create a test script for vision_bridge integration."""
    test_script_path = base_dir / "test_vision_bridge_sam2.py"
    
    print(f"\n📝 Creating vision bridge test script: {test_script_path}")
    
    test_content = f'''#!/usr/bin/env python3
"""
Test script for SAM 2 integration with vision_bridge
"""

import os
import sys
import numpy as np

# Add SAM 2 repository to path
sys.path.insert(0, "{sam2_repo_dir.absolute()}")

# Set environment variables (adjust paths as needed)
os.environ['SAM_CHECKPOINT'] = os.path.abspath('./checkpoints/sam2.1_hiera_large.pt')
os.environ['SAM_CONFIG'] = os.path.abspath('./sam2_repo/configs/sam2.1/sam2.1_hiera_l.yaml')

def test_sam2_integration():
    """Test SAM 2 integration with vision_bridge style code."""
    print("🧪 Testing SAM 2 integration...")
    
    try:
        # Import SAM 2
        from sam2.build_sam import build_sam2
        from sam2.sam2_image_predictor import SAM2ImagePredictor
        import torch
        
        print("✅ SAM 2 imports successful")
        
        # Test model loading
        checkpoint = os.environ['SAM_CHECKPOINT']
        config = os.environ['SAM_CONFIG']
        
        if not os.path.exists(checkpoint):
            print(f"❌ Checkpoint not found: {{checkpoint}}")
            return False
            
        if not os.path.exists(config):
            print(f"❌ Config not found: {{config}}")
            return False
        
        # Build model
        model = build_sam2(config, checkpoint)
        device = "cuda" if torch.cuda.is_available() else "cpu"
        model.to(device)
        predictor = SAM2ImagePredictor(model)
        
        print(f"✅ SAM 2 model loaded on {{device}}")
        
        # Test with dummy image
        dummy_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        predictor.set_image(dummy_image)
        
        # Test prediction with dummy box
        input_box = np.array([100, 100, 200, 200])
        masks, scores, _ = predictor.predict(
            box=input_box[None, :],
            multimask_output=False
        )
        
        print(f"✅ SAM 2 prediction successful")
        print(f"   Mask shape: {{masks[0].shape}}")
        print(f"   Score: {{scores[0]:.3f}}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {{e}}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_sam2_integration()
    sys.exit(0 if success else 1)
'''
    
    with open(test_script_path, 'w') as f:
        f.write(test_content)
    
    test_script_path.chmod(0o755)
    print(f"✅ Test script created: {test_script_path}")
    return test_script_path

def print_usage_instructions(base_dir, env_script, test_script, model_info):
    """Print usage instructions."""
    print(f"\n{'='*70}")
    print("🎉 SAM 2 Setup Complete!")
    print(f"{'='*70}")
    
    print(f"\n📋 Setup Summary:")
    print(f"   Model: SAM 2.1 {model_info['checkpoint']}")
    print(f"   Description: {model_info['description']}")
    print(f"   Base directory: {base_dir}")
    print(f"   Environment script: {env_script}")
    print(f"   Test script: {test_script}")
    
    print(f"\n🚀 Usage Instructions:")
    print(f"1. Source the environment script:")
    print(f"   source {env_script}")
    print(f"")
    print(f"2. Test the installation:")
    print(f"   python {test_script}")
    print(f"")
    print(f"3. Use with vision_bridge:")
    print(f"   cd /home/hafnium/aloha-lite/vision_bridge")
    print(f"   source {env_script}")
    print(f"   python beaker_analysis.py")
    print(f"")
    print(f"4. Or set environment variables manually:")
    print(f"   export SAM_CHECKPOINT=\"{base_dir}/checkpoints/{model_info['checkpoint']}\"")
    print(f"   export SAM_CONFIG=\"{base_dir}/sam2_repo/{model_info['config']}\"")
    
    print(f"\n💡 Notes:")
    print(f"   • The vision_bridge will automatically use SAM 2 when checkpoint is available")
    print(f"   • Falls back to circle detection if SAM 2 is not configured")
    print(f"   • GPU is recommended for best performance")
    print(f"   • You can switch models by changing SAM_CHECKPOINT and SAM_CONFIG")

def main():
    """Main setup function."""
    print_header()
    
    # Parse command line arguments
    if len(sys.argv) < 2:
        print("Available models:")
        for name, info in SAM2_MODELS.items():
            print(f"  {name:12} - {info['description']} ({info['size_mb']}MB)")
        print(f"\nUsage: {sys.argv[0]} <model_name> [base_directory]")
        print(f"Example: {sys.argv[0]} large")
        return 1
    
    model_name = sys.argv[1]
    base_dir = Path(sys.argv[2] if len(sys.argv) > 2 else "./sam2_setup")
    
    # Create base directory
    base_dir.mkdir(exist_ok=True)
    print(f"📁 Working in: {base_dir.absolute()}")
    
    # Check requirements
    if not check_requirements():
        return 1
    
    # Setup repository
    sam2_repo_dir = setup_sam2_repository(base_dir)
    if not sam2_repo_dir:
        return 1
    
    # Setup model
    model_setup = setup_model(model_name, sam2_repo_dir, base_dir)
    if not model_setup:
        return 1
    
    # Test installation
    if not test_sam2_installation(sam2_repo_dir, model_setup):
        print("⚠️  Installation test failed, but files are set up. You can try manual testing.")
    
    # Create helper scripts
    env_script = create_environment_script(base_dir, model_setup, sam2_repo_dir)
    test_script = create_test_script(base_dir, sam2_repo_dir)
    
    # Print usage instructions
    print_usage_instructions(base_dir, env_script, test_script, model_setup['model_info'])
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
