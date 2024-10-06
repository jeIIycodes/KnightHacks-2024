
from collections import Counter



class MostCommonModel:
    def __init__(self):
        self.most_common_accelerators = []

    def train(self, train_interactions):
        # Find the most common accelerators
        accelerator_counts = Counter(train_interactions)
        self.most_common_accelerators = [acc for acc, count in accelerator_counts.most_common()]

    def recommend(self, top_n=5):
        return self.most_common_accelerators[:top_n]



