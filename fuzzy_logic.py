import math

class FBN:
    """
    Translates raw numerical sensory data into fuzzy linguistic labels.
    Zero-dependency implementation.
    """
    @staticmethod
    def triangular(x, a, b, c):
        """Triangular membership function."""
        if x <= a or x >= c:
            return 0.0
        if a < x <= b:
            return (x - a) / (b - a)
        if b < x < c:
            return (c - x) / (c - b)
        return 0.0

    @staticmethod
    def trapezoidal(x, a, b, c, d):
        """Trapezoidal membership function."""
        if x <= a or x >= d:
            return 0.0
        if a < x <= b:
            return (x - a) / (b - a)
        if b < x <= c:
            return 1.0
        if c < x < d:
            return (d - x) / (d - c)
        return 0.0

    def __init__(self):
        pass

    def fuzzify_distance(self, dist):
        """Fuzzifies a distance value (0 to ~14)."""
        return {
            'CERCA': self.trapezoidal(dist, 0, 0, 1.2, 2.5),
            'MEDIA': self.triangular(dist, 1.5, 3, 5),
            'LEJOS': self.trapezoidal(dist, 4, 6, 20, 20)
        }

    def fuzzify_hunger(self, val):
        """Fuzzifies hunger/tiredness (0 to 150)."""
        return {
            'BAJO': self.trapezoidal(val, 0, 0, 30, 60),
            'MEDIO': self.triangular(val, 40, 75, 110),
            'ALTO': self.trapezoidal(val, 90, 120, 200, 200)
        }

    def fuzzify_battery(self, dist):
        """Fuzzifies battery proximity."""
        if dist is None: # No battery detected
            return {'MUY_CERCA': 0, 'LEJOS': 0, 'AUSENTE': 1.0}
        
        return {
            'MUY_CERCA': self.trapezoidal(dist, 0, 0, 1.5, 3.0),
            'LEJOS': self.trapezoidal(dist, 2.0, 5.0, 20, 20),
            'AUSENTE': 0.0
        }

    def process_state(self, robot_state):
        """
        Converts full robot state into a vector of fuzzy membership degrees.
        Returns a dictionary of dictionaries.
        """
        raw_perception = robot_state['raw_distances'] # To be implemented in robot.py
        hunger = robot_state['needs']['hunger']
        tiredness = robot_state['needs']['tiredness']
        batt_dist = robot_state['batt_distance']

        fuzzy_state = {}
        
        # Wall Distances in 4 directions
        for direction, dist in raw_perception.items():
            fuzzy_state[f'MURO_{direction}'] = self.fuzzify_distance(dist)
            
        fuzzy_state['HAMBRE'] = self.fuzzify_hunger(hunger)
        fuzzy_state['CANSANCIO'] = self.fuzzify_hunger(tiredness)
        fuzzy_state['BATERIA'] = self.fuzzify_battery(batt_dist)
        
        return fuzzy_state

    def get_fuzzy_vector(self, robot_state):
        """
        Returns a flat list of (feature_name:label) for rules.
        Only returns features with membership > 0.
        """
        f_state = self.process_state(robot_state)
        vector = []
        for category, memberships in f_state.items():
            for label, degree in memberships.items():
                if degree > 0:
                    vector.append(f"{category}:{label}")
        return sorted(vector)

    def get_feature_vector(self, robot_state):
        """Alias for compatibility."""
        return self.get_fuzzy_vector(robot_state)
