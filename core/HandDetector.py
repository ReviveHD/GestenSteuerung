import mediapipe as mp
import os
import cv2 as cv

class HandDetector:
    """Kapselt die MediaPipe-Logik für die Erkennung von bis zu 2 Händen."""

    def __init__(self, model_name='Models/hand_landmarker.task'):
        self.result = None
        self.timestamp_counter = 0

        # Pfad-Auflösung
        base_path = os.path.dirname(os.path.dirname(__file__))
        model_path = os.path.join(base_path, model_name)

        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model-Datei fehlt: {model_path}")

        # MediaPipe Konfiguration
        options = mp.tasks.vision.HandLandmarkerOptions(
            base_options=mp.tasks.BaseOptions(model_asset_path=model_path),
            running_mode=mp.tasks.vision.RunningMode.LIVE_STREAM,
            num_hands=2,
            min_hand_detection_confidence=0.7,
            result_callback=self._save_result
        )
        self.landmarker = mp.tasks.vision.HandLandmarker.create_from_options(options)

    def _save_result(self, result, output_image, timestamp_ms):
        self.result = result

    def detect(self, frame):
        # MediaPipe benötigt RGB
        rgb_frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        self.timestamp_counter += 1
        self.landmarker.detect_async(mp_image, self.timestamp_counter)

    def get_all_hands(self):
        """Gibt Landmarks und Seite (Links/Rechts) für alle Hände zurück."""
        hands_list = []
        if self.result and self.result.hand_landmarks:
            for i, landmarks in enumerate(self.result.hand_landmarks):
                label = self.result.handedness[i][0].category_name
                hands_list.append({"landmarks": landmarks, "label": label})
        return hands_list



    def close(self):
        self.landmarker.close()