import pickle
from models.matrix_SGD.matrix_sgd import MatrixFactorization
from models.ensemble.item_knn_baseline import ItemKNNBaseline
from models.ensemble.user_knn_baseline import UserKNNBaseline
from models.ensemble.meta_model import MetaModel
import pandas as pd
import numpy as np

class EnsembleModel:
    def __init__(self, mf_params=None, item_knn_k=30, user_knn_k=30, alpha=1.0):
        """
        mf_params: params for MatrixFactorization {'n_factors': int, 'n_epochs': int, 'lr': float, 'reg': float}
        item_knn_k: neighbors number for ItemKNNBaseline
        user_knn_k: neighbors number for UserKNNBaseline
        alpha: ridge fro MetaModel (Ridge)
        """
        self.mf_params = mf_params or {'n_factors': 15, 'n_epochs': 35, 'lr': 0.005, 'reg': 0.01}
        self.item_knn_k = item_knn_k
        self.user_knn_k = user_knn_k
        self.alpha = alpha

        self.mf_model = None
        self.item_knn_model = None
        self.user_knn_model = None
        self.meta_model = None

    def fit(self, train_data: pd.DataFrame):
        print("Training MatrixFactorization...")
        self.mf_model = MatrixFactorization(train_data, **self.mf_params)
        self.mf_model.fit()

        print("Trainingм ItemKNNBaseline...")
        self.item_knn_model = ItemKNNBaseline(k=self.item_knn_k)
        self.item_knn_model.fit(train_data)

        print("Training UserKNNBaseline...")
        self.user_knn_model = UserKNNBaseline(k=self.user_knn_k)
        self.user_knn_model.fit(train_data)

        print("Training MetaModel (stacking)...")
        base_models = {
            'matrix': self.mf_model,
            'item_knn': self.item_knn_model,
            'user_knn': self.user_knn_model
        }
        self.meta_model = MetaModel(base_models=base_models, alpha=self.alpha)
        self.meta_model.fit(train_data)

    def predict(self, user_id, movie_id):
        if self.meta_model is None:
            raise ValueError("Model didn't train. First use fit()")
        return self.meta_model.predict(user_id, movie_id)

    def evaluate(self, test_data: pd.DataFrame):
        errors = []
        squared_errors = []
        for row in test_data.itertuples():
            pred = self.predict(row.user_id, row.movie_id)
            true = row.rating
            errors.append(abs(pred - true))
            squared_errors.append((pred - true) ** 2)
        mae = np.mean(errors)
        rmse = np.sqrt(np.mean(squared_errors))
        return mae, rmse

    def save(self, path):
        with open(path, 'wb') as f:
            pickle.dump(self, f)

    @staticmethod
    def load(path):
        with open(path, 'rb') as f:
            return pickle.load(f)
        