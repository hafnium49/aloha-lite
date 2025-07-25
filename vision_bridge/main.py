# vision_bridge/main.py
import os, uuid, io, datetime, logging, math
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx, boto3
import numpy as np, cv2, torch                            # ← NEW
from prometheus_client import Counter, start_http_server
from sklearn.cluster import KMeans
from matplotlib import colors
import base64

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────────────────
# Optional: SAM 2 (Segment Anything Model 2)
# ──────────────────────────────────────────────────────────────────────────
SAM_PREDICTOR = None
try:
    from sam2.build_sam import build_sam2
    from sam2.sam2_image_predictor import SAM2ImagePredictor
    SAM_CKPT = os.getenv("SAM_CHECKPOINT", "/models/sam2.1_hiera_large.pt")
    SAM_CONFIG = os.getenv("SAM_CONFIG", "configs/sam2.1/sam2.1_hiera_l.yaml")
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

# ---------------------------------------------------------------------------
# Environment (make optional for testing)
# ---------------------------------------------------------------------------
PHOS_URL = os.getenv("PHOS_URL", "http://phosphobot")
BUCKET   = os.getenv("BUCKET", "snapshots")

# Only require S3 variables if they're needed (for production)
if os.getenv("REQUIRE_S3", "true").lower() == "true":
    required_env_vars = ["S3_ENDPOINT", "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"]
    for var in required_env_vars:
        if not os.getenv(var):
            logger.error(f"{var} environment variable is required")
            raise ValueError(f"{var} environment variable is required")

    s3 = boto3.client(
        "s3",
        endpoint_url=os.getenv("S3_ENDPOINT"),
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    )
else:
    s3 = None

# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------
SNAP_OK   = Counter("cam_snapshot_ok_total",   "Snapshots succeeded")
SNAP_ERR  = Counter("cam_snapshot_err_total",  "Snapshots failed")
CIRCLE_OK = Counter("circle_detect_ok_total",  "Circle detections succeeded")
CIRCLE_ERR= Counter("circle_detect_err_total", "Circle detections failed")

# Only start Prometheus server if not in testing mode
if not os.environ.get('TESTING', '').lower() == 'true':
    start_http_server(9003)

# ---------------------------------------------------------------------------
# FastAPI
# ---------------------------------------------------------------------------
app = FastAPI(title="Vision‑Bridge")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],         # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Enhanced beaker color detection algorithm
# ---------------------------------------------------------------------------
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
    h, w = image_data.shape[:2]
    img_center_x, img_center_y = w // 2, h // 2

    # Convert to grayscale and blur for circle detection
    gray = cv2.cvtColor(image_data, cv2.COLOR_BGR2GRAY)
    gray_blur = cv2.GaussianBlur(gray, (9, 9), 2)

    # Detect circles (the beaker opening) with improved parameters for center detection
    circles = cv2.HoughCircles(
        gray_blur, cv2.HOUGH_GRADIENT, 
        dp=1.2, 
        minDist=max(30, min(w, h) // 8),  # Adaptive minimum distance
        param1=100, 
        param2=25,  # Slightly lower threshold for better detection
        minRadius=max(20, min(w, h) // 20),  # Adaptive minimum radius
        maxRadius=min(300, min(w, h) // 3)   # Adaptive maximum radius
    )
    
    if circles is None:
        raise ValueError("No beaker detected")

    # Improved circle selection: combine size and proximity to center
    circles = np.uint16(np.around(circles[0]))
    
    def score_circle(circle):
        """Score circles based on size and proximity to image center."""
        cx, cy, radius = circle
        
        # Distance from image center (normalized by image diagonal)
        center_dist = math.sqrt((cx - img_center_x)**2 + (cy - img_center_y)**2)
        max_dist = math.sqrt(img_center_x**2 + img_center_y**2)  # Max possible distance
        center_score = 1.0 - (center_dist / max_dist)  # Higher score for center proximity
        
        # Size score (normalized by max possible radius)
        size_score = radius / min(w, h) * 2  # Normalize to 0-1 range
        
        # Combined score: 70% center proximity, 30% size
        combined_score = 0.7 * center_score + 0.3 * size_score
        
        return combined_score
    
    # Score all circles and select the best one
    scored_circles = [(score_circle(c), c) for c in circles]
    best_score, (x, y, r) = max(scored_circles, key=lambda x: x[0])
    
    # Log detection details for debugging
    logger.info(f"Beaker detection: found {len(circles)} circles, selected ({x}, {y}, r={r}) with score {best_score:.3f}")
    logger.info(f"Image center: ({img_center_x}, {img_center_y}), selected distance from center: {math.sqrt((x - img_center_x)**2 + (y - img_center_y)**2):.1f}")
    
    # Optional: Add validation that the best circle is reasonably centered
    center_distance = math.sqrt((x - img_center_x)**2 + (y - img_center_y)**2)
    max_acceptable_distance = min(w, h) * 0.3  # Allow up to 30% of image size from center
    
    if center_distance > max_acceptable_distance:
        # Look for a more centered alternative
        centered_circles = [c for c in circles 
                          if math.sqrt((c[0] - img_center_x)**2 + (c[1] - img_center_y)**2) <= max_acceptable_distance]
        if centered_circles:
            # Among centered circles, pick the largest
            old_x, old_y, old_r = x, y, r
            x, y, r = max(centered_circles, key=lambda c: c[2])
            logger.info(f"Fallback to centered circle: ({old_x}, {old_y}, r={old_r}) -> ({x}, {y}, r={r})")

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
    
    # A. Draw the detected beaker circle
    circle = analysis_data['beaker_circle']
    cv2.circle(viz_img, (circle['x'], circle['y']), circle['radius'], (0, 255, 0), 3)
    
    # Draw center point
    cv2.circle(viz_img, (circle['x'], circle['y']), 5, (0, 255, 0), -1)

    # B.  If a SAM mask was returned, overlay it in translucent yellow
    if analysis_data.get("sam_mask_preview") is not None:
        sam_alpha = 0.35
        yellow    = np.array([0, 255, 255], dtype=np.uint8)
        mask_bool = analysis_data["sam_mask_preview"] > 0
        viz_img[mask_bool] = cv2.addWeighted(viz_img, 1-sam_alpha,
                                             np.full_like(viz_img, yellow), sam_alpha, 0)[mask_bool]
    
    # Add text with dominant color info
    dominant_cluster = next(c for c in analysis_data['clusters'] 
                          if c['index'] == analysis_data['dominant_cluster_index'])
    
    text = f"Dominant Color: RGB{tuple(dominant_cluster['color_rgb'])}"
    cv2.putText(viz_img, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    saturation_text = f"Saturation: {dominant_cluster['avg_saturation']:.1f}"
    cv2.putText(viz_img, saturation_text, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    return viz_img


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------
class SnapReq(BaseModel):
    cmd_id: str
    cam_id: str = "top_cam"

# ---------------------------------------------------------------------------
# Snapshot endpoint (unchanged)
# ---------------------------------------------------------------------------
@app.post("/snapshot")
async def snapshot(req: SnapReq):
    ts   = datetime.datetime.utcnow().isoformat(timespec="seconds")
    key  = f"{req.cmd_id}/{req.cam_id}_{ts}.jpg"
    url  = f"{PHOS_URL}/camera/snapshot/{req.cam_id}?format=jpeg"

    try:
        async with httpx.AsyncClient(timeout=10.0) as cl:
            r = await cl.get(url)
            if r.status_code != 200:
                SNAP_ERR.inc()
                logger.error(f"Camera error: {r.status_code}")
                raise HTTPException(502, f"Camera error: {r.status_code}")

            data = io.BytesIO(r.content)
            if s3:
                s3.upload_fileobj(
                    data,
                    BUCKET,
                    key,
                    ExtraArgs={"ContentType": "image/jpeg"},
                )

        SNAP_OK.inc()
        if s3:
            presigned = s3.generate_presigned_url(
                "get_object",
                Params={"Bucket": BUCKET, "Key": key},
                ExpiresIn=86_400,
            )
            return {"url": presigned}
        else:
            return {"url": f"http://localhost/snapshots/{key}"}  # fallback URL

    except httpx.TimeoutException:
        SNAP_ERR.inc()
        logger.error("Timeout calling camera")
        raise HTTPException(504, "Timeout calling camera")
    except Exception as e:
        SNAP_ERR.inc()
        logger.error(f"Error taking snapshot: {e}")
        raise HTTPException(500, f"Snapshot error: {str(e)}")

# ---------------------------------------------------------------------------
# NEW: circle‑colour endpoint
# ---------------------------------------------------------------------------
@app.post("/circle-colour")
async def circle_colour(file: UploadFile = File(...)):
    """
    Detect the most prominent circle in the *left half* of the image
    and return the average colour inside the circle.

    Response JSON:
    {
        "circle": {"center": [x, y], "radius": r},
        "mean_color": {
            "bgr": [b, g, r],
            "rgb": [r, g, b],
            "hex": "#RRGGBB"
        }
    }
    """
    try:
        # ------------------------------------------------------------------
        # Decode image
        # ------------------------------------------------------------------
        data = await file.read()
        arr  = np.frombuffer(data, np.uint8)
        img  = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if img is None:
            raise HTTPException(400, "Invalid image format")

        h, w = img.shape[:2]
        img_center_x, img_center_y = w // 2, h // 2
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray, 5)

        # ------------------------------------------------------------------
        # Improved Hough‑circle detection with center weighting
        # ------------------------------------------------------------------
        circles = cv2.HoughCircles(
            gray,
            cv2.HOUGH_GRADIENT,
            dp=1.2,
            minDist=max(30, h // 8),  # Adaptive minimum distance
            param1=100,
            param2=25,  # Slightly lower threshold for better detection
            minRadius=int(min(h, w) * 0.05),
            maxRadius=int(min(h, w) * 0.4),
        )

        if circles is None:
            CIRCLE_ERR.inc()
            logger.warning("No circles detected")
            raise HTTPException(422, "No circle detected")

        circles = np.round(circles[0, :]).astype(int)

        def score_circle_legacy(circle):
            """Score circles for legacy endpoint with center preference."""
            cx, cy, radius = circle
            
            # Distance from image center
            center_dist = math.sqrt((cx - img_center_x)**2 + (cy - img_center_y)**2)
            max_dist = math.sqrt(img_center_x**2 + img_center_y**2)
            center_score = 1.0 - (center_dist / max_dist)
            
            # Size score
            size_score = radius / min(w, h) * 2
            
            # Left-side preference (legacy behavior)
            left_score = 1.0 if cx < w // 2 else 0.7
            
            # Combined score: 50% center, 30% size, 20% left preference
            combined_score = 0.5 * center_score + 0.3 * size_score + 0.2 * left_score
            
            return combined_score

        # Score all circles and select the best one
        scored_circles = [(score_circle_legacy(c), c) for c in circles]
        best_score, (cx, cy, r) = max(scored_circles, key=lambda x: x[0])
        
        # Fallback to center-proximity if no good left-side circles
        center_distance = math.sqrt((cx - img_center_x)**2 + (cy - img_center_y)**2)
        max_acceptable_distance = min(w, h) * 0.35  # Allow up to 35% from center
        
        if center_distance > max_acceptable_distance:
            # Look for more centered alternatives
            centered_circles = [c for c in circles 
                              if math.sqrt((c[0] - img_center_x)**2 + (c[1] - img_center_y)**2) <= max_acceptable_distance]
            if centered_circles:
                cx, cy, r = max(centered_circles, key=lambda c: c[2])

        # Sanity‑check radius
        r = int(max(1, min(r, w, h)))

        # ------------------------------------------------------------------
        # Mask & colour statistics
        # ------------------------------------------------------------------
        mask = np.zeros((h, w), dtype=np.uint8)
        cv2.circle(mask, (cx, cy), r, 255, -1)

        mean_bgr = cv2.mean(img, mask=mask)[:3]  # ignore alpha
        mean_bgr = [int(round(c)) for c in mean_bgr]
        mean_rgb = mean_bgr[::-1]
        mean_hex = "#{:02X}{:02X}{:02X}".format(*mean_rgb)

        CIRCLE_OK.inc()
        return {
            "circle": {"center": [int(cx), int(cy)], "radius": int(r)},
            "mean_color": {"bgr": mean_bgr, "rgb": mean_rgb, "hex": mean_hex},
        }

    except HTTPException:
        raise
    except Exception as e:
        CIRCLE_ERR.inc()
        logger.error(f"Error detecting circle/colour: {e}")
        raise HTTPException(500, f"Circle detection error: {str(e)}")


# ---------------------------------------------------------------------------
# NEW: Enhanced beaker solution color detection endpoint
# ---------------------------------------------------------------------------
@app.post("/analyze-beaker")
async def analyze_beaker(file: UploadFile = File(...)):
    """
    Advanced beaker analysis using Hough Circle Transform and K-Means clustering
    to automatically detect the beaker and extract the dominant solution color.
    
    Response JSON:
    {
        "dominant_color": {
            "rgb": [r, g, b],
            "hex": "#RRGGBB"
        },
        "beaker_circle": {"x": x, "y": y, "radius": r},
        "clusters": [...],
        "analysis_stats": {...},
        "visualization_image": "base64_encoded_image"
    }
    """
    try:
        # Decode image
        data = await file.read()
        arr = np.frombuffer(data, np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if img is None:
            raise HTTPException(400, "Invalid image format")

        # Perform enhanced beaker color analysis
        dominant_color_rgb, dominant_color_hex, analysis_data = extract_solution_color(img)
        
        # Create visualization
        viz_img = create_visualization_image(img, analysis_data)
        
        # Encode visualization image to base64
        _, buffer = cv2.imencode('.jpg', viz_img)
        viz_base64 = base64.b64encode(buffer).decode('utf-8')
        
        # Prepare response - convert numpy types to Python types
        clusters_json = []
        for cluster in analysis_data['clusters']:
            clusters_json.append({
                "rgb": [int(cluster['color_rgb'][0]), int(cluster['color_rgb'][1]), int(cluster['color_rgb'][2])],
                "hex": colors.to_hex(cluster['color_rgb'] / 255),
                "saturation": float(cluster['avg_saturation']),
                "pixel_count": int(cluster['pixel_count']),
                "index": int(cluster['index'])
            })
        
        response = {
            "dominant_color": {
                "rgb": [int(dominant_color_rgb[0]), int(dominant_color_rgb[1]), int(dominant_color_rgb[2])],
                "hex": dominant_color_hex
            },
            "beaker_circle": {
                "x": int(analysis_data['beaker_circle']['x']),
                "y": int(analysis_data['beaker_circle']['y']),
                "radius": int(analysis_data['beaker_circle']['radius'])
            },
            "clusters": clusters_json,
            "analysis_stats": {
                "total_pixels_analyzed": int(analysis_data['total_pixels_analyzed']),
                "num_clusters": len(analysis_data['clusters']),
                "dominant_cluster_index": int(analysis_data['dominant_cluster_index'])
            },
            "visualization_image": viz_base64
        }
        
        CIRCLE_OK.inc()
        logger.info(f"Beaker analysis successful: {dominant_color_hex}")
        return response

    except ValueError as e:
        CIRCLE_ERR.inc()
        logger.warning(f"Beaker analysis failed: {e}")
        raise HTTPException(422, str(e))
    except Exception as e:
        CIRCLE_ERR.inc()
        logger.error(f"Error in beaker analysis: {e}")
        raise HTTPException(500, f"Beaker analysis error: {str(e)}")
