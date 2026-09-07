"""
Step 3 - Personal AI Trainer: counts repetitions (curls / push-ups) from the
elbow angle using PoseModule.

Run:  python 02_ai_trainer.py               (webcam)
      python 02_ai_trainer.py video.mp4     (video file)
Press 'q' to quit.

Landmarks used (MediaPipe Pose):
    Right arm: 12 (shoulder), 14 (elbow), 16 (wrist)
    Left arm : 11 (shoulder), 13 (elbow), 15 (wrist)
Change SIDE below to track the other arm.
"""
import sys

import cv2
import numpy as np

from PoseModule import poseDetector

SIDE = "right"  # "right" or "left"
LANDMARKS = {"right": (12, 14, 16), "left": (11, 13, 15)}
ANGLE_EXTENDED = 160  # arm straight
ANGLE_FLEXED = 90     # arm bent

source = sys.argv[1] if len(sys.argv) > 1 else 0
cap = cv2.VideoCapture(source)
if not cap.isOpened():
    print(f"Error: could not open video source: {source}")
    sys.exit(1)

detector = poseDetector()
direction = 0  # 0 = going down/bent next, 1 = going up/extend next
count = 0.0

while True:
    success, img = cap.read()
    if not success:
        break

    img = cv2.resize(img, (1280, 720))
    img = detector.findPose(img, draw=False)
    lmList = detector.findPosition(img, draw=False)

    if lmList:
        raw = detector.findAngle(img, *LANDMARKS[SIDE])
        angle = min(raw, 360 - raw)  # inner angle 0-180, independent of arm orientation

        # progress bar value: 0% (extended) -> 100% (fully flexed)
        per = float(np.interp(angle, (ANGLE_FLEXED, ANGLE_EXTENDED), (100, 0)))
        bar = int(np.interp(per, (0, 100), (650, 100)))

        # count a full rep = flex then extend
        if angle < ANGLE_FLEXED and direction == 0:
            count += 0.5
            direction = 1
        if angle > ANGLE_EXTENDED and direction == 1:
            count += 0.5
            direction = 0

        # progress bar
        cv2.rectangle(img, (1100, 100), (1175, 650), (0, 255, 0), 3)
        cv2.rectangle(img, (1100, bar), (1175, 650), (0, 255, 0), cv2.FILLED)
        cv2.putText(img, f"{int(per)}%", (1080, 85), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 3)

        # rep counter
        cv2.rectangle(img, (0, 560), (200, 720), (0, 255, 0), cv2.FILLED)
        cv2.putText(img, str(int(count)), (45, 670), cv2.FONT_HERSHEY_PLAIN, 8, (255, 0, 0), 12)

    cv2.imshow("AI Trainer", img)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
