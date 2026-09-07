# AI Trainer - Web Application

Real-time personal trainer in the browser: pose estimation, automatic rep counting
(bicep curl, squat, push-up), and a backend that saves your workout history and stats.

## Architecture
- **Frontend** (`frontend/index.html`): webcam + MediaPipe Pose Landmarker running in the
  browser (video never leaves your computer). Draws the skeleton, computes joint angles,
  counts reps, shows a live progress bar, timer, weekly chart and history.
- **Backend** (`backend/main.py`): FastAPI + SQLite. REST API to save, list and delete
  workouts and compute stats. Also serves the frontend.
- **desktop/**: the original OpenCV scripts (PoseModule, basic demo, trainer). They need
  `pip install opencv-python mediapipe numpy`.

## Run
```bash
python -m venv venv
venv\Scripts\activate            # Windows  (source venv/bin/activate on macOS/Linux)
pip install -r requirements.txt
uvicorn backend.main:app --reload
```
Open http://localhost:8000 (camera access works on localhost or HTTPS only).
The first start needs internet to download the MediaPipe scripts and model from CDN.

## API
| Method | Endpoint | Purpose |
|---|---|---|
| POST | /api/workouts | Save a session `{exercise, reps, duration_sec}` |
| GET | /api/workouts?limit=20 | Recent sessions |
| DELETE | /api/workouts/{id} | Delete a session |
| GET | /api/stats | Totals, reps per exercise, last 7 days |

Interactive docs: http://localhost:8000/docs

## Tips
Stand 2-3 m from the camera with your side or front fully visible and good lighting.
Angle thresholds per exercise are in the `EX` object in `frontend/index.html`.

## Ideas for next steps
User accounts, video-upload analysis using `desktop/PoseModule.py`, more exercises,
form feedback and voice cues, Docker deployment.
