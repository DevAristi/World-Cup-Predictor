class TournamentSimulator:
    def __init__(self, model, pipeline, groups):
        self.model = model
        self.pipeline = pipeline
        self.groups = groups
        self.match_cache = {}