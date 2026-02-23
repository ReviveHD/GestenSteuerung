class EMAFilter:
    def __init__(self, alpha=0.2):
        """
        alpha: Wert zwischen 0 und 1.
        Kleiner = glatter, aber langsamer.
        Größer = schneller, aber zittriger.
        """
        self.alpha = alpha
        self.prev_value = None

    def apply(self, current_value):
        if self.prev_value is None:
            self.prev_value = current_value
            return current_value

        # Die Formel: Neuer Wert = (Gewicht * Neu) + (Rest * Alt)
        filtered_value = (self.alpha * current_value) + (1 - self.alpha) * self.prev_value
        self.prev_value = filtered_value
        return filtered_value