
from core.HandDetector import HandDetector
from core.GestureEngine import GestureEngine
import cv2 as cv

# --- Hauptprogramm (Die Verbindung) ---
if __name__ == "__main__":
    detector = HandDetector()
    engine = GestureEngine()
    cap = cv.VideoCapture(0)

    while cap.isOpened():
        success, frame = cap.read()
        if not success: break

        frame = cv.flip(frame, 1)  # Spiegeln
        h, w, _ = frame.shape

        detector.detect(frame)
        hands = detector.get_all_hands()

        for hand in hands:
            lms = hand["landmarks"]
            side = hand["label"]

            # 1. Finger-Code holen (z.B. [0, 1, 0, 0, 0])
            finger_code = engine.get_finger_state(lms)

            # 2. Geste benennen
            gesture_name = engine.parse_gesture(finger_code)

            # 3. Zeichnen
            color = (0, 255, 0) if side == "Right" else (255, 0, 255)
            # Zeichne Fingerspitzen zur Kontrolle
            for tid in [4, 8, 12, 16, 20]:
                cx, cy = int(lms[tid].x * w), int(lms[tid].y * h)
                cv.circle(frame, (cx, cy), 8, color, cv.FILLED)

            # Info-Text
            y_offset = 50 if side == "Right" else 100
            cv.putText(frame, f"{side}: {gesture_name} {finger_code}", (20, y_offset),
                       cv.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

        cv.imshow('Multi-Hand Gesture System', frame)
        if cv.waitKey(1) & 0xFF == ord('q'): break

    detector.close()
    cap.release()
    cv.destroyAllWindows()