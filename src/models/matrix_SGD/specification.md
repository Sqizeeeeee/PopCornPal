# Matrix Factorization Model

This model implements **Matrix Factorization** for movie recommendations by learning latent factors from user ratings.

## How It Works

1. **Data Preparation**  
   The model maps unique user and movie IDs to indices and initializes latent factor matrices and bias terms.

2. **Latent Factor Training**  
   It trains user and item latent factors along with user and item biases via stochastic gradient descent, minimizing the regularized squared error over observed ratings.

3. **Rating Prediction**  
   For a user-item pair, the predicted rating is computed as the sum of the global average rating, user bias, item bias, and the dot product of user and item latent factors. The prediction is clipped to the valid rating range (1 to 5).

4. **Cold-Start Handling**  
   If the user or movie is unknown, the model returns the global mean rating as a fallback.

5. **Model Hyperparameters**  
   The model uses configurable parameters such as number of latent factors, learning rate, regularization strength, and number of training epochs.

## Best Parameters Found

- **Number of latent factors:** 20  
- **Learning rate:** 0.01  
- **Regularization (reg):** 0.1  
- **Number of epochs:** 20  

These parameters were used during training and showed effective convergence.

# Performance Metrics

### MAE = 0.6827
### RSME = 0.8774

## Attempts to Find the Best Parameters

### Attempt 1:

- **n_factors_list** = [20, 40, 60]  
- **n_epochs_list** = [25, 35, 45, 60]  
- **Learning rate (r)** = 0.005  
- **Regularization (reg)** = 0.01  

### Summary of Results:

| Factors | Epochs | MAE    | RMSE   |
|---------|--------|--------|--------|
| 20      | 25     | 0.6864 | 0.8797 |
| 20      | 35     | 0.6857 | 0.8831 |
| 20      | 45     | 0.6861 | 0.8858 |
| 20      | 60     | 0.6876 | 0.8904 |
| 40      | 25     | 0.6954 | 0.8927 |
| 40      | 35     | 0.7015 | 0.9064 |
| 40      | 45     | 0.7060 | 0.9154 |
| 40      | 60     | 0.7147 | 0.9299 |
| 60      | 25     | 0.7001 | 0.9006 |
| 60      | 35     | 0.7112 | 0.9202 |
| 60      | 45     | 0.7214 | 0.9370 |
| 60      | 60     | 0.7295 | 0.9504 |
