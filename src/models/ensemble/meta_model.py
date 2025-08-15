import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge

class MetaModel:
    def __init__(self, base_models: dict, params=None):
        self.base_models = base_models
        self.params = params or {'alpha': 1.0}  # параметр регуляризации Ridge
        self.model = Ridge(**self.params)
        self.fitted = False

    def fit(self, train_data: pd.DataFrame):
        X, y = self._build_features(train_data)
        self.model.fit(X, y)
        self.fitted = True

    def predict(self, user_id, movie_id):
        if not self.fitted:
            raise ValueError("MetaModel не обучен! Сначала вызовите fit().")
        features = np.array([m.predict(user_id, movie_id) for m in self.base_models.values()]).reshape(1, -1)
        pred = self.model.predict(features)[0]
        return np.clip(pred, 1, 5)

    def _build_features(self, data: pd.DataFrame):
        X = []
        y = []
        for row in data.itertuples():
            features = [m.predict(row.user_id, row.movie_id) for m in self.base_models.values()]
            X.append(features)
            y.append(row.rating)
        return np.array(X), np.array(y)