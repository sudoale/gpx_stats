class Course:

    def __init__(self, name):
        self.name = name
        self.distance = 0
        self.ascent = 0
        self.descent = 0
        self.segments = []
        self._reset_metrics()

    def _reset_metrics(self):
        self.labels = []
        self.distances = []
        self.ascents = []
        self.descents = []
        self.steepnesses = []
        self.elevations = []
        self.elevation_labels = []

    def add_segment(self, segment):
        self.segments.append(segment)
        self._update_from_segements()

    def add_segments(self, segments):
        for s in segments:
            self.add_segment(s)

    def _update_from_segements(self):
        self._reset_metrics()
        for i, s in enumerate(self.segments):
            self.labels.append(s.label)
            self.distances.append(s.distance)
            self.ascents.append(s.ascent)
            self.descents.append(s.descent)
            self.steepnesses.append(s.steepness)
            self.elevations.extend(s.elevation)
            self.elevation_labels.extend([i] * len(s.elevation))
        self.distance = sum(self.distances)
        self.ascent = sum(self.ascents)
        self.descent = sum(self.descents)
