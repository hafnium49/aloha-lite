# vision_bridge/main.py
import os, uuid, io, datetime, logging, math
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx, boto3
import numpy as np, cv2
from prometheus_client import Counter, start_http_server

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------
PHOS_URL = os.getenv("PHOS_URL", "http://phosphobot")
BUCKET   = os.getenv("BUCKET", "snapshots")

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

# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------
SNAP_OK   = Counter("cam_snapshot_ok_total",   "Snapshots succeeded")
SNAP_ERR  = Counter("cam_snapshot_err_total",  "Snapshots failed")
CIRCLE_OK = Counter("circle_detect_ok_total",  "Circle detections succeeded")
CIRCLE_ERR= Counter("circle_detect_err_total", "Circle detections failed")
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
            s3.upload_fileobj(
                data,
                BUCKET,
                key,
                ExtraArgs={"ContentType": "image/jpeg"},
            )

        SNAP_OK.inc()
        presigned = s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": BUCKET, "Key": key},
            ExpiresIn=86_400,
        )
        return {"url": presigned}

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
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray, 5)

        # ------------------------------------------------------------------
        # Hough‑circle detection
        # ------------------------------------------------------------------
        circles = cv2.HoughCircles(
            gray,
            cv2.HOUGH_GRADIENT,
            dp=1.2,
            minDist=h // 4,
            param1=100,
            param2=30,
            minRadius=int(min(h, w) * 0.05),
            maxRadius=int(min(h, w) * 0.4),
        )

        if circles is None:
            CIRCLE_ERR.inc()
            logger.warning("No circles detected")
            raise HTTPException(422, "No circle detected")

        circles = np.round(circles[0, :]).astype(int)

        # Keep only circles whose centre is in the left half
        left_circles = [c for c in circles if c[0] < w // 2]
        if not left_circles:
            left_circles = circles.tolist()

        # Choose the largest radius among remaining circles
        cx, cy, r = max(left_circles, key=lambda c: c[2])

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
