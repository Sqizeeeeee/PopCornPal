import sys
import os
import pickle

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import pandas as pd
from data_preparation import prepare_data
from models.user_based.user_based_cf import UserBasedCF

def main():
    train_data, test_data, movies, user_index, movie_index = prepare_data()

    print(f"Train size: {len(train_data)}, Test size: {len(test_data)}")

    model_dir = 'src/models/user_based'
    os.makedirs(model_dir, exist_ok=True)
    model_path = os.path.join(model_dir, 'user_based_cf_model.pkl')

    if os.path.exists(model_path):
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        print("Model loaded from file")
    else:
        model = UserBasedCF(train_data, k=25, similarity_threshold=0.2)
        model.fit()
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)
        print("Model trained and saved")

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

    print(f"MAE on testing data: {mae:.4f}")
    print(f"RMSE on testing data: {rmse:.4f}")

    user_id = test_data['user_id'].iloc[0]
    recommendations = model.recommend(user_id, n=10)
    print(f"Top-10 recommendations for user {user_id}:")
    for movie_id, rating in recommendations:
        print(f"Film ID: {movie_id}, Predicted rating: {rating:.2f}")

if __name__ == "__main__":
    main()