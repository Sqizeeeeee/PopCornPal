import os
import sys
import pickle
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from data_preparation import prepare_data
from models.matrix_SGD.matrix_sgd import MatrixFactorization

def main():
    train_data, test_data, movies, user_index, movie_index = prepare_data()

    print(f"Train size: {len(train_data)}, Test size: {len(test_data)}")

    n_factors_list = [20, 40, 60]
    n_epochs_list = [25, 35, 45, 60]
    lr = 0.005
    reg = 0.01

    results = []

    for n_factors in n_factors_list:
        for n_epochs in n_epochs_list:
            print(f"\nTraining model with n_factors={n_factors}, n_epochs={n_epochs}")
            model = MatrixFactorization(train_data, n_factors=n_factors, n_epochs=n_epochs, lr=lr, reg=reg)
            model.fit()

            errors = []
            squared_errors = []
            total = len(test_data)

            for i, (_, row) in enumerate(test_data.iterrows(), 1):
                pred = model.predict(row['user_id'], row['movie_id'])
                true = row['rating']
                errors.append(abs(pred - true))
                squared_errors.append((pred - true) ** 2)
                if i % (total // 10) == 0:
                    print(f"Processed {i} of {total} ({(i / total) * 100:.0f}%)")

            mae = sum(errors) / len(errors)
            rmse = (sum(squared_errors) / len(squared_errors)) ** 0.5

            print(f"MAE: {mae:.4f}, RMSE: {rmse:.4f}")
            results.append((n_factors, n_epochs, mae, rmse))

    print("\nSummary of results:")
    for n_factors, n_epochs, mae, rmse in results:
        print(f"Factors: {n_factors}, Epochs: {n_epochs} => MAE: {mae:.4f}, RMSE: {rmse:.4f}")

    # Можно добавить сохранение лучшей модели, если хочешь

if __name__ == "__main__":
    main()


if __name__ == "__main__":
    main()