import os
import sys
import pickle
import pandas as pd


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from data_preparation import prepare_data
from models.item_based.item_based_cf import ItemBasedCF  # Твоя новая модель item-based

def main():
    train_data, test_data, movies, user_index, movie_index = prepare_data()

    print(f"Train size: {len(train_data)}, Test size: {len(test_data)}")

    model = ItemBasedCF(train_data, k=20, similarity_threshold=0.15)
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

    print(f"MAE on testing data: {mae:.4f}")
    print(f"RMSE on testing data: {rmse:.4f}")

    save_answer = input("Save model? (y/n): ").strip().lower()
    if save_answer == 'y':
        model_path = 'src/models/item_based/item_based_cf_model.pkl'
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)
        print(f"Model saved to {model_path}")
    else:
        print("Model not saved.")

if __name__ == "__main__":
    main()