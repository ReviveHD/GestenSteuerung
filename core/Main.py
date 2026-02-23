
from core.HandDetector import HandDetector
from core.GestureEngine import GestureEngine
import cv2 as cv
from Actions.SpotifyAPI import SpotifyAPIStrategy
from utils.filters import EMAFilter
import time
import config



# --- Hauptprogramm (Die Verbindung) ---
if __name__ == "__main__":
    detector = HandDetector()
    engine = GestureEngine()
    cap = cv.VideoCapture(0)
    spotify_action = SpotifyAPIStrategy()
    volume_filter = EMAFilter(alpha=0.15)  # Schön glatt eingestellt
    last_volume_time = 0
    last_sent_volume = -1
    VOLUME_COOLDOWN = 0.7  # Sicherheitsabstand für die Spotify API
    system_active = False
    toggle_cooldown = 0
    last_toggle_time = 0
    gesture_threshold = 5  # Wie viele Frames muss die Geste stabil sein?
    gesture_counter = 0
    current_gesture = "UNKNOWN"

    last_command_time = 0
    COOLDOWN_DURATION = 5  # 1.5 Sekunden warten zwischen Gesten
    last_gesture = "UNKNOWN"

    while cap.isOpened():
        success, frame = cap.read()
        if not success: break

        #frame = cv.flip(frame, 1)  # Spiegeln
        h, w, _ = frame.shape

        detector.detect(frame)
        hands = detector.get_all_hands()

        for hand in hands:
            lms = hand["landmarks"]
            finger_code = engine.get_finger_state(lms)

            # Geste für Hang Loose: Daumen(1), Kleiner(1), Rest(0)
            if finger_code == [1, 0, 0, 0, 1] and not last_gesture == "HANG_LOOSE":
                current_time = time.time()
                # Geste muss 1 Sekunde gehalten werden, um zu toggeln
                if not system_active and current_time - last_toggle_time > 5 or system_active:
                    if current_time - last_toggle_time > 2.0:

                        system_active = not system_active
                        last_toggle_time = current_time
                        if system_active:
                            last_gesture = "HANG_LOOSE"
                        print(f"SYSTEM STATUS: {'AKTIV' if system_active else 'STANDBY'}")

        # 2. Visuelles Feedback (Wichtig, damit du weißt, ob du gerade steuerst)
        status_color = (0, 255, 0) if system_active else (0, 0, 255)
        status_text = "MODUS: AKTIV" if system_active else "MODUS: STANDBY"
        cv.putText(frame, status_text, (50, 50), cv.FONT_HERSHEY_SIMPLEX, 1, status_color, 3)

        if system_active:
            for hand in hands:
                lms = hand["landmarks"]
                finger_code = engine.get_finger_state(lms)



                detected_gesture = engine.parse_gesture(finger_code)

                current_time = time.time()
                time_passed = current_time - last_command_time

                # 1. Stabilitäts-Check
                if detected_gesture == current_gesture:
                    gesture_counter += 1
                else:
                    # Geste hat sich geändert -> Zähler zurücksetzen
                    current_gesture = detected_gesture
                    gesture_counter = 0
                if gesture_counter >= gesture_threshold:
                    if current_gesture in ["PEACE", "POINTING", "FIST", "OPEN_HAND"] and hand["label"] == "Right":
                        # if time_passed > config.GESTURE_COOLDOWN:
                        if current_gesture != last_gesture:

                            # BEFEHL AUSFÜHREN
                            print(f"Löse Aktion aus: {current_gesture} für {hand['label']}")

                            if hand["label"] == "Right":
                                spotify_action.execute_gesture(current_gesture)

                            # Zeit und Geste merken
                            last_command_time = current_time
                            last_gesture = current_gesture

                            gesture_counter = 0

                    # Beispiel-Geste: Nur Daumen (0) und Zeigefinger (1) sind oben
                    elif finger_code == [1, 1, 0, 0, 0] and hand["label"] == "Right":

                        # 1. Rohwert holen
                        raw_volume = engine.get_pinch_distance(lms)

                        # 2. Filtern (Zittern entfernen)
                        smoothed_volume = int(volume_filter.apply(raw_volume))

                        # 3. Zeit- und Schwellenwert-Check (API schützen)
                        current_time = time.time()

                        # Nur senden, wenn:
                        # - Genug Zeit vergangen ist
                        # - UND sich der geglättete Wert um mindestens 4% geändert hat
                        if current_time - last_volume_time > VOLUME_COOLDOWN:
                            if abs(smoothed_volume - last_sent_volume) >= 4:
                                spotify_action.set_volume(smoothed_volume)

                                last_sent_volume = smoothed_volume
                                last_volume_time = current_time

                        # Feedback im Bild anzeigen
                        cv.putText(frame, f"Filter Vol: {smoothed_volume}%", (50, 150),
                                cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                        pass

                    elif current_gesture == "UNKNOWN":
                        last_gesture = "UNKNOWN"


        cv.imshow('Multi-Hand Gesture System', frame)
        if cv.waitKey(1) & 0xFF == ord('q'): break




    detector.close()
    cap.release()
    cv.destroyAllWindows()