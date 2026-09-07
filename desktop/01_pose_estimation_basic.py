"""
Step 1 - Basic pose estimation with MediaPipe (no custom module).
Run:  python 01_pose_estimation_basic.py path/to/video.mp4
      python 01_pose_estimation_basic.py 0        (webcam)
Press 'q' to quit.
"""
import sys
import time

import cv2
import mediapipe as mp

source = sys.argv[1] if len(sys.argv) > 1 else "PoseVideos/1.mp4"
source = 0 if source == "0" else source

mpDraw = mp.solutions.drawing_utils
mpPose = mp.solutions.pose
pose = mpPose.Pose()

cap = cv2.VideoCapture(source)
if not cap.isOpened():
    print(f"Error: could not open video source: {source}")
    sys.exit(1)

pTime = 0
cv2.namedWindow("Image", cv2.WINDOW_NORMAL)

while True:
    success, img = cap.read()
    if not success:
        print("End of video / failed to read frame")
        break

    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = pose.process(imgRGB)

    if results.pose_landmarks:
        mpDraw.draw_landmarks(img, results.pose_landmarks, mpPose.POSE_CONNECTIONS)
        h, w, _ = img.shape
        for id, lm in enumerate(results.pose_landmarks.landmark):
            cx, cy = int(lm.x * w), int(lm.y * h)
            cv2.circle(img, (cx, cy), 5, (255, 0, 0), cv2.FILLED)

    cTime = time.time()
    fps = 1 / (cTime - pTime) if pTime else 0
    pTime = cTime
    cv2.putText(img, str(int(fps)), (70, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)

    cv2.imshow("Image", img)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
