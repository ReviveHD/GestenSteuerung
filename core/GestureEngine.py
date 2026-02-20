import math

class GestureEngine:
    """Berechnet aus Landmarks Fingerzustände und Gesten."""

    def __init__(self):
        self.tip_ids = [8, 12, 16, 20]  # Zeige, Mittel, Ring, Kleiner

    def get_finger_state(self, landmarks):
        fingers = []

        # 1. Referenzwert: Handflächen-Länge (Handwurzel 0 bis Mittelfinger-Ansatz 9)
        # Dieser Wert dient uns als "Maßstab"
        palm_size = self.calculate_dist(landmarks[0], landmarks[9])

        # 2. Daumen (Abstand Spitze 4 zu Kleinfinger-Wurzel 17)
        thumb_dist = self.calculate_dist(landmarks[4], landmarks[13])
        fingers.append(0 if (thumb_dist / palm_size) < 0.6 else 1)

        # 3. Die anderen Finger (Abstand Spitze zu Handwurzel 0)
        # IDs der Spitzen: Zeige(8), Mittel(12), Ring(16), Kleiner(20)
        # Wir erwarten, dass ein ausgestreckter Finger etwa 1.5 - 2.0-mal so lang
        # ist wie die Handfläche (palm_size).
        tips = [8, 12, 16, 20]
        for tip_id in tips:
            dist = self.calculate_dist(landmarks[tip_id], landmarks[0])
            # Wenn der Abstand Spitze-zu-Wurzel deutlich größer als die Handfläche ist
            if (dist / palm_size) > 1.3:
                fingers.append(1)
            else:
                fingers.append(0)

        return fingers

    def parse_gesture(self, finger_list):
        gestures = {
            (0, 1, 0, 0, 0): "POINTING",
            (0, 1, 1, 0, 0): "PEACE",
            (1, 1, 1, 1, 1): "OPEN_HAND",
            (0, 0, 0, 0, 0): "FIST",
            (1, 0, 0, 0, 1): "HANG_LOOSE",
            (1, 1, 0, 0, 1): "ROCK N' ROLL",
        }
        return gestures.get(tuple(finger_list), "UNKNOWN")

    def calculate_dist(self, p1, p2):
        """Berechnet den euklidischen Abstand zwischen zwei Landmarks."""
        return math.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2)