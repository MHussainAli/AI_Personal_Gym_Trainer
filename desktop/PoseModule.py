"""
PoseModule.py
Reusable pose-detection class built on MediaPipe Pose + OpenCV.

Usage:
    from PoseModule import poseDetector
    detector = poseDetector()
    img = detector.findPose(img)
    lmList = detector.findPosition(img, draw=False)
    angle = detector.findAngle(img, 12, 14, 16)
"""
import math
import sys
import time

import cv2
import mediapipe as mp


class poseDetector:
    def __init__(
        self,
        static_image_mode=False,
        model_complexity=1,
        enable_segmentation=False,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    ):
        self.static_image_mode = static_image_mode  # False = video stream
        self.model_complexity = model_complexity  # 0, 1 or 2 (higher = more accurate, slower)
        self.enable_segmentation = enable_segmentation
        self.min_detection_confidence = min_detection_confidence
        self.min_tracking_confidence = min_tracking_confidence

        self.mpDraw = mp.solutions.drawing_utils
        self.mpPose = mp.solutions.pose
        self.pose = self.mpPose.Pose(
            static_image_mode=self.static_image_mode,
            model_complexity=self.model_complexity,
            enable_segmentation=self.enable_segmentation,
            min_detection_confidence=self.min_detection_confidence,
            min_tracking_confidence=self.min_tracking_confidence,
        )
        self.results = None
        self.lmList = []

    def findPose(self, img, draw=True):
        """Detect the pose in a BGR image and optionally draw the skeleton."""
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.pose.process(imgRGB)
        if self.results.pose_landmarks and draw:
            self.mpDraw.draw_landmarks(
                img, self.results.pose_landmarks, self.mpPose.POSE_CONNECTIONS
            )
        return img

    def findPosition(self, img, draw=True):
        """Return a list of [id, x, y] pixel positions for the 33 landmarks."""
        self.lmList = []
        if self.results and self.results.pose_landmarks:
            h, w, _ = img.shape
            for id, lm in enumerate(self.results.pose_landmarks.landmark):
                cx, cy = int(lm.x * w), int(lm.y * h)
                self.lmList.append([id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 5, (255, 0, 0), cv2.FILLED)
        return self.lmList

    def findAngle(self, img, p1, p2, p3, draw=True):
        """Angle (0-360 degrees) at landmark p2 formed by p1-p2-p3."""
        x1, y1 = self.lmList[p1][1:]
        x2, y2 = self.lmList[p2][1:]
        x3, y3 = self.lmList[p3][1:]

        angle = math.degrees(
            math.atan2(y3 - y2, x3 - x2) - math.atan2(y1 - y2, x1 - x2)
        )
        if angle < 0:
            angle += 360

        if draw:
            cv2.line(img, (x1, y1), (x2, y2), (255, 255, 255), 3)
            cv2.line(img, (x3, y3), (x2, y2), (255, 255, 255), 3)
            for (x, y) in ((x1, y1), (x2, y2), (x3, y3)):
                cv2.circle(img, (x, y), 10, (0, 0, 255), cv2.FILLED)
                cv2.circle(img, (x, y), 15, (0, 0, 255), 2)
            cv2.putText(
                img, str(int(angle)), (x2 - 50, y2 + 50),
                cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2,
            )
        return angle


def main(source="PoseVideos/1.mp4"):
    """Quick demo: run the detector on a video file (or 0 for webcam)."""
    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        print(f"Error: could not open video source: {source}")
        return

    detector = poseDetector()
    pTime = 0
    cv2.namedWindow("Image", cv2.WINDOW_NORMAL)

    while True:
        success, img = cap.read()
        if not success:
            print("End of video / failed to read frame")
            break

        img = detector.findPose(img)
        lmList = detector.findPosition(img, draw=False)
        if lmList:
            print(lmList[14])  # right elbow
            cv2.circle(img, (lmList[14][1], lmList[14][2]), 15, (0, 0, 255), cv2.FILLED)

        cTime = time.time()
        fps = 1 / (cTime - pTime) if pTime else 0
        pTime = cTime
        cv2.putText(img, str(int(fps)), (70, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)

        cv2.imshow("Image", img)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else "PoseVideos/1.mp4"
    main(0 if src == "0" else src)
