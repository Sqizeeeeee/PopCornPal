# User-Based Collaborative Filtering Model

This model implements **User-Based Collaborative Filtering** for movie recommendations based on historical user ratings.

## How It Works

1. **User-Item Matrix Construction**  
   The model builds a user-item matrix from the ratings data, where rows represent users and columns represent movies. Missing ratings are filled with zeros.

2. **User Similarity Calculation**  
   It calculates similarities between users using **cosine similarity**, which measures how similar their rating patterns are.

3. **Rating Prediction**  
   To predict a rating for a given user and movie, the model:  
   - Identifies other users ("neighbors") with similar tastes who have rated the target movie.  
   - Considers only neighbors whose similarity exceeds a predefined threshold.  
   - Uses up to `k` nearest neighbors to compute a weighted average rating, where weights are the similarity scores.

4. **Cold-Start & Fallbacks**  
   If the user or movie is new or if no suitable neighbors are found, the model returns the average rating either for the user (if available) or globally.

5. **Recommendations**  
   The model recommends the top-n movies with the highest predicted ratings for a user, focusing on movies the user hasn’t rated yet.

## Best Parameters Found

- **k (number of neighbors):** 25  
- **Similarity threshold (minimum user similarity cutoff):** 0.2  

These values showed optimal performance during training.