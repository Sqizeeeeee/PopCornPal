import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import pandas as pd
from data_preparation import prepare_data
from models.user_based.user_based_cf import UserBasedCF

def main():
    train_data, test_data, movies, user_index, movie_index = prepare_data()

    print(f"Train size: {len(train_data)}, Test size: {len(test_data)}")

    model = UserBasedCF(train_data, k=25, similarity_threshold=0.1)
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
            print(f"Обработано {i} из {total} ({(i / total) * 100:.0f}%)")

    mae = sum(errors) / len(errors)
    rmse = (sum(squared_errors) / len(squared_errors)) ** 0.5

    print(f"MAE on testing data: {mae:.4f}")
    print(f"RMSE on testing data: {rmse:.4f}")

    user_id = test_data['user_id'].iloc[0]
    recommendations = model.recommend(user_id, n=10)
    print(f"top-10 recomendations for user {user_id}:")
    for movie_id, rating in recommendations:
        print(f"Film ID: {movie_id}, Predicted rating: {rating:.2f}")

if __name__ == "__main__":
    main()