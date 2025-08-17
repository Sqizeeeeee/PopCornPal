# Ensemble

These ensemble implements item-based and user-based K-Nearest Neighbors (KNN) recommendation systems, respectively, both incorporating mean ratings to improve prediction accuracy.

## How They Work

### ItemKNNWithMeans

1. **Data Preparation**  
   - Builds a user-item rating matrix from the training data.  
   - Computes mean ratings per user and per item.  
   - Fills missing ratings with zeros for similarity calculation.

2. **Similarity Computation**  
   - Calculates cosine similarity between items (movies) based on their filled rating vectors.

3. **Rating Prediction**  
   - If the movie is unknown, returns the user’s mean rating or a default value.  
   - For known movies, finds movies rated by the user.  
   - Computes similarity weights between the target movie and these movies.  
   - Applies the "WithMeans" formula: predicted rating = item mean + weighted sum of user’s deviations from item means among neighbors.  
   - Clips prediction within the allowed rating range (1 to 5).

4. **Parameter**  
   - `k`: Number of neighbor items considered (default 20).

---

### UserKNNWithMeans

1. **Training**  
   - Builds a user-item rating matrix from the input data.  
   - Computes mean ratings per user and the global mean rating.  
   - Fills missing values with zeros for computing similarity.  
   - Calculates cosine similarity between users.

2. **Rating Prediction**  
   - Returns the global mean if the user or movie is unknown.  
   - Finds users who rated the target movie.  
   - Identifies the top-`k` most similar users to the target user.  
   - Predicts the rating as a weighted average of these users’ ratings, weighted by similarity.  
   - Clips the predicted rating to the range 1 to 5.

3. **Parameter**  
   - `k`: Number of neighbor users considered (default 20).

---

Both models handle missing data by using mean ratings and use cosine similarity as a measure of closeness. They provide personalized rating predictions via weighted aggregation of neighbors’ ratings adjusted by mean biases.

# Attempts to Find the Best Parameters

## Matrix Factorization

- **n_factors_list** = [15, 20, 25]   
- **Learning rate (r)** = [0.005, 0.01 ] 
- **Regularization (reg)** = [0.01, 0.05]  

### Summary of Results:
| LR    | Factors | Reg   | MAE    | RMSE   |
|-------|---------|-------|--------|--------|
| 0.005 | 15      | 0.01  | 0.7363 | 0.9304 |
| 0.005 | 15      | 0.05  | 0.7353 | 0.9269 |
| 0.005 | 20      | 0.01  | 0.7373 | 0.9315 |
| 0.005 | 20      | 0.05  | 0.7353 | 0.9271 |
| 0.005 | 25      | 0.01  | 0.7380 | 0.9326 |
| 0.005 | 25      | 0.05  | 0.7357 | 0.9273 |
| 0.01  | 15      | 0.01  | 0.7567 | 0.9653 |
| 0.01  | 15      | 0.05  | 0.7375 | 0.9326 |
| 0.01  | 20      | 0.01  | 0.7644 | 0.9753 |
| 0.01  | 20      | 0.05  | 0.7378 | 0.9330 |
| 0.01  | 25      | 0.01  | 0.7664 | 0.9781 |
| 0.01  | 25      | 0.05  | 0.7388 | 0.9347 |


### Inference:
The best parameters are:
- **n_factors_list** = 20
- **Learning rate (r)** = 0.005
- **Regularization (reg)** = 0.05

# MAE = 0.6727
# RMSE = 0.8569


## Item KNN Model
The best parameters are:
- **k** = 20

# MAE = 0.7096




# Results:
## Now I'm having an ensemble of 2 models with MAE = 0.6777. They both work perfectly. I'm not able to delete Item KNN model to improve MAE metric cause of working with "cold users"


