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

- **Number of latent factors:** 15  
- **Learning rate:** 0.01  
- **Regularization (reg):** 0.1  
- **Number of epochs:** 20  

These parameters were used during training and showed effective convergence.

# Performance Metrics

### MAE = 0.6827
### RSME = 0.8774

# Attempts to Find the Best Parameters

## Attempt 1:

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

![Graphic1](/src/graphics/matrixmodel/attempt1.png)

### Inference:
The best parameters are:
- **n_factors_list** = [15, 18, 20, 22, 25]
- **n_epochs_list** = [20, 23, 25, 28, 30, 33, 35]
- **Learning rate (r)** = 0.005
- **Regularization (reg)** = 0.01



## Attempt 2:

- **n_factors_list** = [15, 18, 20, 22, 25]  
- **n_epochs_list** = [20, 23, 25, 28, 30, 33, 35]  
- **Learning rate (r)** = 0.005  
- **Regularization (reg)** = 0.01 


### Summary of Results:
| Factors | Epochs | MAE    | RMSE   |
|---------|--------|--------|--------|
| 15      | 20     | 0.6876 | 0.8770 |
| 15      | 23     | 0.6864 | 0.8769 |
| 15      | 25     | 0.6847 | 0.8762 |
| 15      | 28     | 0.6829 | 0.8753 |
| 15      | 30     | 0.6822 | 0.8755 |
| 15      | 33     | 0.6830 | 0.8773 |
| 15      | 35     | 0.6812 | 0.8756 |
| 18      | 20     | 0.6901 | 0.8800 |
| 18      | 23     | 0.6871 | 0.8789 |
| 18      | 25     | 0.6866 | 0.8784 |
| 18      | 28     | 0.6843 | 0.8782 |
| 18      | 30     | 0.6846 | 0.8792 |
| 18      | 33     | 0.6853 | 0.8809 |
| 18      | 35     | 0.6842 | 0.8807 |
| 20      | 20     | 0.6890 | 0.8790 |
| 20      | 23     | 0.6869 | 0.8791 |
| 20      | 25     | 0.6856 | 0.8784 |
| 20      | 28     | 0.6844 | 0.8787 |
| 20      | 30     | 0.6860 | 0.8806 |
| 20      | 33     | 0.6850 | 0.8817 |
| 20      | 35     | 0.6837 | 0.8802 |
| 22      | 20     | 0.6901 | 0.8807 |
| 22      | 23     | 0.6873 | 0.8791 |
| 22      | 25     | 0.6865 | 0.8794 |
| 22      | 28     | 0.6865 | 0.8816 |
| 22      | 30     | 0.6862 | 0.8823 |
| 22      | 33     | 0.6862 | 0.8832 |
| 22      | 35     | 0.6870 | 0.8850 |
| 25      | 20     | 0.6899 | 0.8804 |
| 25      | 23     | 0.6875 | 0.8807 |
| 25      | 25     | 0.6893 | 0.8838 |
| 25      | 28     | 0.6882 | 0.8840 |
| 25      | 30     | 0.6878 | 0.8850 |
| 25      | 33     | 0.6889 | 0.8872 |
| 25      | 35     | 0.6904 | 0.8902 |


![Graphic2](/src/graphics/matrixmodel/attempt2.png)