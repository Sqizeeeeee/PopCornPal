import pandas as pd
import numpy as np
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from data_preparation import prepare_data
from models.matrix_SGD.matrix_sgd import MatrixFactorization
from models.ensemble.item_knn_baseline import ItemKNNBaseline
from models.ensemble.user_knn_baseline import UserKNNBaseline
from models.ensemble.meta_model import MetaModel
from sklearn.model_selection import ParameterGrid

def evaluate_model(model, test_data):
    errors = []
    squared_errors = []
    for row in test_data.itertuples():
        pred = model.predict(row.user_id, row.movie_id)
        true = row.rating
        errors.append(abs(pred - true))
        squared_errors.append((pred - true) ** 2)
    mae = np.mean(errors)
    rmse = np.sqrt(np.mean(squared_errors))
    return mae, rmse

def main():
    # Загружаем данные
    train_data, test_data, movies, user_index, movie_index = prepare_data()
    print(f"Train size: {len(train_data)}, Test size: {len(test_data)}\n")

# -----------------------------
# 1. Подбор MatrixFactorization
# -----------------------------
    print("Обучаем MatrixFactorization на полном датасете...")
    mf_param_grid = {
        'n_factors': [20, 25, 30],
        'lr': [0.005, 0.01],
        'reg': [0.01, 0.05],
        'n_epochs': [40]  # используем фиксированное количество эпох
    }

    best_mae_mf = float('inf')
    best_params_mf = None
    best_mf_model = None

    for params in ParameterGrid(mf_param_grid):
        mf_model = MatrixFactorization(
            train_data,
            n_factors=params['n_factors'],
            lr=params['lr'],
            reg=params['reg'],
            n_epochs=params['n_epochs']
        )
        mf_model.fit()
        mae, rmse = evaluate_model(mf_model, test_data)
        print(f"MF {params} => MAE: {mae:.4f}, RMSE: {rmse:.4f}")
        if mae < best_mae_mf:
            best_mae_mf = mae
            best_params_mf = params
            best_mf_model = mf_model

    print(f"\nЛучшие параметры MF: {best_params_mf}, MAE={best_mae_mf:.4f}\n")

    # -----------------------------
    # 2. ItemKNNBaseline
    # -----------------------------
    print("Обучаем ItemKNNBaseline...")
    best_mae_item = float('inf')
    best_k_item = None
    for k in [20, 30, 40]:
        model = ItemKNNBaseline(k=k)
        model.fit(train_data)
        mae, rmse = evaluate_model(model, test_data)
        print(f"ItemKNN k={k} => MAE: {mae:.4f}")
        if mae < best_mae_item:
            best_mae_item = mae
            best_k_item = k
            best_item_model = model
    print(f"Лучший ItemKNN k={best_k_item}, MAE={best_mae_item:.4f}\n")

    # -----------------------------
    # 3. UserKNNBaseline
    # -----------------------------
    print("Обучаем UserKNNBaseline...")
    best_mae_user = float('inf')
    best_k_user = None
    for k in [20, 30, 40]:
        model = UserKNNBaseline(k=k)
        model.fit(train_data)
        mae, rmse = evaluate_model(model, test_data)
        print(f"UserKNN k={k} => MAE: {mae:.4f}")
        if mae < best_mae_user:
            best_mae_user = mae
            best_k_user = k
            best_user_model = model
    print(f"Лучший UserKNN k={best_k_user}, MAE={best_mae_user:.4f}\n")

    # -----------------------------
    # 4. MetaModel (стэкинг)
    # -----------------------------
    print("Обучаем MetaModel...")
    base_models = {
        'matrix': mf_model,
        'item_knn': best_item_model,
        'user_knn': best_user_model
    }
    param_grid = {'alpha': [0.1, 1.0, 10.0]}
    best_mae_meta = float('inf')
    best_alpha = None

    for params in ParameterGrid(param_grid):
        meta_model = MetaModel(base_models=base_models, alpha=params['alpha'])
        meta_model.fit(train_data)
        mae, rmse = evaluate_model(meta_model, test_data)
        print(f"MetaModel alpha={params['alpha']} => MAE: {mae:.4f}")
        if mae < best_mae_meta:
            best_mae_meta = mae
            best_alpha = params['alpha']

    print(f"\nЛучший MetaModel: alpha={best_alpha}, MAE={best_mae_meta:.4f}")

if __name__ == "__main__":
    main()