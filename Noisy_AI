import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

def init_params():
    W1 = np.random.randn(32, 9) * 0.1
    b1 = np.zeros((32, 1))
    W2 = np.random.randn(32, 32) * 0.1
    b2 = np.zeros((32, 1))
    W3 = np.random.randn(9, 32) * 0.1
    b3 = np.zeros((9, 1))
    return W1, b1, W2, b2, W3, b3

def ReLU(Z):
    return np.where(Z > 0, Z, Z * 0.3)

def ReLU_deriv(Z):
    return np.where(Z > 0, 1.0, 0.3)

def forward_prop(W1, b1, W2, b2, W3, b3, X):
    Z1 = W1.dot(X) + b1
    A1 = ReLU(Z1)
    
    Z2 = W2.dot(A1) + b2
    A2 = ReLU(Z2)
    
    Z3 = W3.dot(A2) + b3
    A3 = Z3
    
    return Z1, A1, Z2, A2, Z3, A3

def backward_prop(Z1, A1, Z2, A2, W1, W2, W3, A3, Z3, X, Y):
    dZ3 = A3 - Y
    dW3 = dZ3.dot(A2.T)
    db3 = np.sum(dZ3, axis=1, keepdims=True)
    
    dZ2 = W3.T.dot(dZ3) * ReLU_deriv(Z2)
    dW2 = dZ2.dot(A1.T)
    db2 = np.sum(dZ2, axis=1, keepdims=True)
    
    dZ1 = W2.T.dot(dZ2) * ReLU_deriv(Z1)
    dW1 = dZ1.dot(X.T)
    db1 = np.sum(dZ1, axis=1, keepdims=True)
    
    return dW1, db1, dW2, db2, dW3, db3

def update_params(W1, b1, W2, b2, dW1, db1, dW2, db2, dW3, db3, W3, b3, alpha):
    W1 = W1 - alpha * dW1
    b1 = b1 - alpha * db1    
    W2 = W2 - alpha * dW2  
    b2 = b2 - alpha * db2 
    W3 = W3 - alpha * dW3  
    b3 = b3 - alpha * db3    
    return W1, b1, W2, b2, W3, b3

def gradient_descent(X, Y, W1, b1, W2, b2, W3, b3, alpha, iterations):
    for i in range(iterations):
        Z1, A1, Z2, A2, Z3, A3 = forward_prop(W1, b1, W2, b2, W3, b3, X)
        dW1, db1, dW2, db2, dW3, db3 = backward_prop(Z1, A1, Z2, A2, W1, W2, W3, A3, Z3, X, Y)
        W1, b1, W2, b2, W3, b3 = update_params(W1, b1, W2, b2, dW1, db1, dW2, db2, dW3, db3, W3, b3, alpha)
    return W1, b1, W2, b2, W3, b3

def make_predictions(X, W1, b1, W2, b2, W3, b3):
    _, _, _, _, _, A3 = forward_prop(W1, b1, W2, b2, W3, b3, X)
    return A3

def predict_price(prices):
    
    maxy = np.mean(prices)
    initial_volatility = max(np.std(prices),maxy * 0.001)
    #delet the max in case
    W1, b1, W2, b2, W3, b3 = init_params()
    
    for i in range(500):
        data = prices
        row_1 = np.array(data[0+i:9+i]).reshape(9,1)
        row_2 = np.array(data[1+i:10+i]).reshape(9,1)
        
        X_dev = row_2 / maxy
        Y_train = row_2 / maxy 
        X_train = row_1 / maxy
        
        W1, b1, W2, b2, W3, b3 = gradient_descent(X_train, Y_train, W1, b1, W2, b2, W3, b3, 0.01, 100)
        
        dev_predictions = make_predictions(X_dev, W1, b1, W2, b2, W3, b3)
        raw_next_val = dev_predictions[8,0].item() * maxy
        
        noise = np.random.normal(0, initial_volatility * 0.4)

        final_next_val = raw_next_val + noise
        
        prices.append(final_next_val)
        
    return prices[10 : len(prices)]
