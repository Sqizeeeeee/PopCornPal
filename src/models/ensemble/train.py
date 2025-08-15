import pandas as pd
import numpy as np
import os
import sys
import joblib
from sklearn.model_selection import ParameterGrid

# Adding path to the project
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from data_preparation import prepare_data
from models.matrix_SGD.matrix_sgd import MatrixFactorization
from models.ensemble.item_knn_baseline import ItemKNNWithMeans
from models.ensemble.meta_model import MetaModel


def evaluate_model(model, test_data):
    """MAE и RMSE for a model."""
    errors = []
    squared_errors = []
    for row in test_data.itertuples():
        pred = model.predict(row.user_id, row.movie_id)
        true = row.rating
        errors.append(abs(pred - true))
        squared_errors.append((pred - true) ** 2)
    mae = np.nanmean(errors)
    rmse = np.sqrt(np.nanmean(squared_errors))
    return mae, rmse


def main():
    # ========================
    # 0. Dowloading data
    # ========================
    train_data, test_data, movies, user_index, movie_index = prepare_data()
    print(f"Train size: {len(train_data)}, Test size: {len(test_data)}\n")

    # ========================
    # 1. MatrixFactorization
    # ========================
    print("Training MatrixFactorization...")
    mf_best_params = {'lr': 0.005, 'n_epochs': 60, 'n_factors': 30, 'reg': 0.05}
    best_mf_model = MatrixFactorization(
        train_data,
        n_factors=mf_best_params['n_factors'],
        lr=mf_best_params['lr'],
        reg=mf_best_params['reg'],
        n_epochs=mf_best_params['n_epochs']
    )
    best_mf_model.fit()
    mae, rmse = evaluate_model(best_mf_model, test_data)
    print(f"MF {mf_best_params} => MAE: {mae:.4f}, RMSE: {rmse:.4f}\n")

    # ========================
    # 2. ItemKNNWithMeans
    # ========================
    print("Training ItemKNNWithMeans...")
    best_item_model = ItemKNNWithMeans(train_data, k=20)
    mae, rmse = evaluate_model(best_item_model, test_data)
    print(f"ItemKNN k=20 => MAE: {mae:.4f}\n")

    # ========================
    # 3. MetaModel (только MF + ItemKNN)
    # ========================
    print("Training MetaModel...")
    base_models = {
        'matrix': best_mf_model,
        'item_knn': best_item_model
    }

    meta_param_grid = {'alpha': [0.1, 1.0, 10.0]}
    best_mae_meta = float('inf')
    best_alpha = None
    best_meta_model = None

    for params in ParameterGrid(meta_param_grid):
        alpha = params['alpha']
        meta_model = MetaModel(base_models=base_models, params={'alpha': alpha})
        meta_model.fit(train_data)
        mae, rmse = evaluate_model(meta_model, test_data)
        print(f"MetaModel alpha={alpha} => MAE: {mae:.4f}")
        if mae < best_mae_meta:
            best_mae_meta = mae
            best_alpha = alpha
            best_meta_model = meta_model

    print(f"\nBest MetaModel: alpha={best_alpha}, MAE={best_mae_meta:.4f}")

    # ========================
    # 4. Saving the best model
    # ========================
    save_path = os.path.join(
        os.path.dirname(__file__), 
        'meta_model.pkl'
    )
    joblib.dump(best_meta_model, save_path)
    print(f"Model saved in: {save_path}")


if __name__ == "__main__":
    main()