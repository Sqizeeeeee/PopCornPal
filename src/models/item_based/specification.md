# Item-Based Collaborative Filtering Model

This model implements **Item-Based Collaborative Filtering** for movie recommendations using historical user ratings.

## How It Works

1. **User-Item Matrix Construction**  
   The model creates a user-item matrix from the ratings data, with users as rows and movies as columns. Ratings are centered by subtracting each movie's average rating; missing values are filled with zeros.

2. **Item Similarity Calculation**  
   It computes similarities between movies using **cosine similarity** on the centered rating vectors.

3. **Rating Prediction**  
   To predict a rating for a given user and movie, the model:  
   - Finds movies similar to the target movie with similarity above a defined threshold.  
   - Uses the target user’s ratings on these similar movies.  
   - Aggregates up to `k` most similar neighbors to compute a weighted average rating, weighted by similarity scores.  
   - Adds back the movie's average rating to de-normalize the prediction.

4. **Cold-Start & Fallbacks**  
   If the user or movie is unknown, or no similar neighbors exist, the model returns the global or movie average rating.

5. **Recommendations**  
   The model can recommend movies with the highest predicted ratings that the user has not yet rated.

## Best Parameters Found

- **k (number of neighbors):** 20  
- **Similarity threshold (minimum item similarity cutoff):** 0.15  

These parameters showed good balance between accuracy and coverage during training.

# MAE and RMSE

### MAE = 0.7366
### RMSE = 0.9513
