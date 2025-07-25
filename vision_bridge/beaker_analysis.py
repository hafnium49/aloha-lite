#!/usr/bin/env python3
"""
Standalone beaker analysis module for testing.
Contains the core beaker color detection algorithms without FastAPI dependencies.
"""

import os
import cv2
import numpy as np
import torch                            # ← NEW
from sklearn.cluster import KMeans
from matplotlib import colors
import base64
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────────────────
# Optional: SAM 2 (Segment Anything Model 2)
# ──────────────────────────────────────────────────────────────────────────
SAM_PREDICTOR = None
try:
    from sam2.build_sam import build_sam2
    from sam2.sam2_image_predictor import SAM2ImagePredictor
    
    # Use local checkpoint and SAM 2 package config
    default_checkpoint = os.path.join(os.path.dirname(__file__), "checkpoints", "sam2.1_hiera_tiny.pt")
    
    SAM_CKPT = os.getenv("SAM_CHECKPOINT", default_checkpoint)
    SAM_CONFIG = os.getenv("SAM_CONFIG", "configs/sam2.1/sam2.1_hiera_t.yaml")  # SAM 2 package config path
    if os.path.exists(SAM_CKPT):
        model = build_sam2(SAM_CONFIG, SAM_CKPT)
        device = "cuda" if torch.cuda.is_available() else "cpu"
        model.to(device)
        SAM_PREDICTOR = SAM2ImagePredictor(model)
        logger.info(f"SAM‑2 loaded from {SAM_CKPT}")
    else:
        logger.warning(f"SAM checkpoint not found ({SAM_CKPT}); SAM disabled")
except ImportError:
    logger.warning("sam2 not installed; SAM disabled")


def extract_solution_color(image_data, n_clusters=5):
    """
    Automatically detect the beaker in the image and return the dominant solution color.
    Uses Hough Circles to locate the beaker and KMeans clustering to identify
    the most saturated cluster inside the beaker.

    Args:
        image_data: numpy array of the image (BGR format from cv2)
        n_clusters: number of clusters for KMeans

    Returns:
        tuple: (dominant_color_rgb, dominant_color_hex, analysis_data)
    """
    image_rgb = cv2.cvtColor(image_data, cv2.COLOR_BGR2RGB)

    # Convert to grayscale and blur for circle detection
    gray = cv2.cvtColor(image_data, cv2.COLOR_BGR2GRAY)
    gray_blur = cv2.GaussianBlur(gray, (9, 9), 2)

    # Detect circles (the beaker opening)
    circles = cv2.HoughCircles(
        gray_blur, cv2.HOUGH_GRADIENT, dp=1.2, minDist=50,
        param1=100, param2=30, minRadius=30, maxRadius=200
    )
    
    if circles is None:
        raise ValueError("No beaker detected")

    # Choose the largest detected circle
    circles = np.uint16(np.around(circles[0]))
    x, y, r = sorted(circles, key=lambda c: c[2], reverse=True)[0]

    # ───────────────────────────────────────────────────────────────────
    # A.  Build a base circular ROI (always available)
    # ───────────────────────────────────────────────────────────────────
    circle_mask = np.zeros_like(gray, dtype=np.uint8)
    cv2.circle(circle_mask, (x, y), r, 255, thickness=-1)

    # ───────────────────────────────────────────────────────────────────
    # B.  Optional SAM‑2 refinement (box‑prompted by the detected circle)
    # ───────────────────────────────────────────────────────────────────
    if SAM_PREDICTOR is not None:
        try:
            SAM_PREDICTOR.set_image(image_rgb)          # SAM expects RGB
            x0, y0 = max(0, x - r), max(0, y - r)
            x1, y1 = min(image_rgb.shape[1]-1, x + r), min(image_rgb.shape[0]-1, y + r)
            input_box = np.array([x0, y0, x1, y1])
            masks, scores, _ = SAM_PREDICTOR.predict(
                box=input_box[None, :],
                multimask_output=False)
            sam_mask = masks[0].astype(np.uint8) * 255   # H×W uint8
            mask = cv2.bitwise_and(circle_mask, sam_mask)
            logger.debug(f"SAM mask IoU≈{scores[0]:.3f}")
        except Exception as e:
            # Fail‑soft: revert to circle‑only mask
            logger.warning(f"SAM failed ({e}); falling back to circle mask")
            mask = circle_mask
    else:
        mask = circle_mask

    masked_img = cv2.bitwise_and(image_rgb, image_rgb, mask=mask)

    # Extract pixel data inside the circle
    pixel_data = masked_img[mask > 0].reshape((-1, 3))

    # Filter out very dark pixels (likely background/shadows)
    brightness_threshold = 30
    bright_pixels = pixel_data[np.sum(pixel_data, axis=1) > brightness_threshold]
    
    if len(bright_pixels) < 10:
        bright_pixels = pixel_data  # fallback to all pixels
    
    # KMeans clustering on the pixel data
    kmeans = KMeans(n_clusters=min(n_clusters, len(bright_pixels)), random_state=42, n_init=10)
    kmeans.fit(bright_pixels)
    centers_rgb = kmeans.cluster_centers_.astype(int)
    labels = kmeans.labels_

    # Convert pixel data to HSV for saturation analysis
    hsv_data = cv2.cvtColor(bright_pixels.reshape((-1, 1, 3)), cv2.COLOR_RGB2HSV).reshape((-1, 3))

    # Compute average saturation for each cluster and pick the highest
    cluster_info = []
    for i in range(len(centers_rgb)):
        cluster_pixels = hsv_data[labels == i]
        if len(cluster_pixels) > 0:
            avg_saturation = cluster_pixels[:, 1].mean()
            avg_value = cluster_pixels[:, 2].mean()
            pixel_count = len(cluster_pixels)
            
            cluster_info.append({
                'index': i,
                'color_rgb': centers_rgb[i],
                'avg_saturation': avg_saturation,
                'avg_value': avg_value,
                'pixel_count': pixel_count,
                'score': avg_saturation * avg_value  # Combined score
            })
    
    # Sort by saturation score and pick the best
    cluster_info.sort(key=lambda x: x['score'], reverse=True)
    dominant_cluster = cluster_info[0]
    
    dominant_color = dominant_cluster['color_rgb']
    dominant_color_hex = colors.to_hex(dominant_color / 255)

    # Prepare analysis data for visualization
    analysis_data = {
        'beaker_circle': {'x': int(x), 'y': int(y), 'radius': int(r)},
        'clusters': cluster_info,
        'dominant_cluster_index': dominant_cluster['index'],
        'total_pixels_analyzed': len(bright_pixels)
    }

    # keep a tiny preview (uint8) for optional visualisation
    analysis_data['sam_mask_preview'] = mask if mask.dtype == np.uint8 else (mask*255).astype(np.uint8)

    return dominant_color, dominant_color_hex, analysis_data


def create_visualization_image(image_data, analysis_data):
    """
    Create a visualization image showing the detected beaker and color analysis.
    
    Args:
        image_data: original image (BGR format)
        analysis_data: analysis results from extract_solution_color
    
    Returns:
        numpy array: visualization image (BGR format)
    """
    viz_img = image_data.copy()
    
    # Draw the detected beaker circle
    circle = analysis_data['beaker_circle']
    cv2.circle(viz_img, (circle['x'], circle['y']), circle['radius'], (0, 255, 0), 3)
    
    # Draw center point
    cv2.circle(viz_img, (circle['x'], circle['y']), 5, (0, 255, 0), -1)
    
    # Add text with dominant color info
    dominant_cluster = next(c for c in analysis_data['clusters'] 
                          if c['index'] == analysis_data['dominant_cluster_index'])
    
    text = f"Dominant Color: RGB{tuple(dominant_cluster['color_rgb'])}"
    cv2.putText(viz_img, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    saturation_text = f"Saturation: {dominant_cluster['avg_saturation']:.1f}"
    cv2.putText(viz_img, saturation_text, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    return viz_img


if __name__ == "__main__":
    """Test the beaker analysis functions with a sample image."""
    import os
    
    sample_image_path = "/home/hafnium/aloha-lite/temporary_images/camera_0_20250723_113227.jpg"
    
    if os.path.exists(sample_image_path):
        print("🧪 Testing beaker analysis functions...")
        
        # Load the test image
        img = cv2.imread(sample_image_path)
        if img is not None:
            try:
                # Perform analysis
                dominant_color, color_hex, analysis_data = extract_solution_color(img)
                
                print(f"✅ Analysis successful!")
                print(f"   Dominant color: {color_hex} RGB{tuple(dominant_color)}")
                print(f"   Beaker position: ({analysis_data['beaker_circle']['x']}, {analysis_data['beaker_circle']['y']})")
                print(f"   Beaker radius: {analysis_data['beaker_circle']['radius']}px")
                print(f"   Clusters found: {len(analysis_data['clusters'])}")
                print(f"   Pixels analyzed: {analysis_data['total_pixels_analyzed']:,}")
                
                # Create visualization
                viz_img = create_visualization_image(img, analysis_data)
                
                # Save visualization in test_results directory
                test_results_dir = "/home/hafnium/aloha-lite/vision_bridge/tests/test_results"
                os.makedirs(test_results_dir, exist_ok=True)
                output_path = os.path.join(test_results_dir, "beaker_analysis_result.jpg")
                cv2.imwrite(output_path, viz_img)
                print(f"   Visualization saved to: {output_path}")
                
            except Exception as e:
                print(f"❌ Analysis failed: {e}")
        else:
            print(f"❌ Could not load image: {sample_image_path}")
    else:
        print(f"❌ Sample image not found: {sample_image_path}")
