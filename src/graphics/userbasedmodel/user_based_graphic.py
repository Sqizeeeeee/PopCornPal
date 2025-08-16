import matplotlib.pyplot as plt

factors = [
    15, 15, 15, 15, 15, 15, 15,
    18, 18, 18, 18, 18, 18, 18,
    20, 20, 20, 20, 20, 20, 20,
    22, 22, 22, 22, 22, 22, 22,
    25, 25, 25, 25, 25, 25, 25
]
epochs = [
    20, 23, 25, 28, 30, 33, 35,
    20, 23, 25, 28, 30, 33, 35,
    20, 23, 25, 28, 30, 33, 35,
    20, 23, 25, 28, 30, 33, 35,
    20, 23, 25, 28, 30, 33, 35
]
mae = [
    0.6876, 0.6864, 0.6847, 0.6829, 0.6822, 0.6830, 0.6812,
    0.6901, 0.6871, 0.6866, 0.6843, 0.6846, 0.6853, 0.6842,
    0.6890, 0.6869, 0.6856, 0.6844, 0.6860, 0.6850, 0.6837,
    0.6901, 0.6873, 0.6865, 0.6865, 0.6862, 0.6862, 0.6870,
    0.6899, 0.6875, 0.6893, 0.6882, 0.6878, 0.6889, 0.6904
]
rmse = [
    0.8770, 0.8769, 0.8762, 0.8753, 0.8755, 0.8773, 0.8756,
    0.8800, 0.8789, 0.8784, 0.8782, 0.8792, 0.8809, 0.8807,
    0.8790, 0.8791, 0.8784, 0.8787, 0.8806, 0.8817, 0.8802,
    0.8807, 0.8791, 0.8794, 0.8816, 0.8823, 0.8832, 0.8850,
    0.8804, 0.8807, 0.8838, 0.8840, 0.8850, 0.8872, 0.8902
]

plt.figure(figsize=(12, 7))

colors = {15: 'blue', 18: 'green', 20: 'red', 22: 'purple', 25: 'orange'}

for factor in sorted(set(factors)):
    idx = [i for i, f in enumerate(factors) if f == factor]
    x = [epochs[i] for i in idx]

    y_mae = [mae[i] for i in idx]
    y_rmse = [rmse[i] for i in idx]

    plt.plot(x, y_mae, marker='o', markersize=2, linestyle='-', color=colors[factor], label=f'MAE (factors={factor})')
    plt.plot(x, y_rmse, marker='x', markersize=3, linestyle='--', color=colors[factor], label=f'RMSE (factors={factor})')

plt.title('MAE and RMSE vs Epochs for Different Number of Factors')
plt.xlabel('Epochs')
plt.ylabel('Error')
plt.legend()
plt.grid(True)
plt.show()
