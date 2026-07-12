import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

def init_params():
    W1 = np.random.rand(6, 9) - 0.5
    b1 = np.random.rand(6, 1) - 0.5
    W2 = np.random.rand(3, 6) - 0.5
    b2 = np.random.rand(3, 1) - 0.5
    W3 = np.random.rand(1, 3) - 0.5
    b3 = np.random.rand(1, 1) - 0.5
    return W1, b1, W2, b2, W3, b3

def ReLU(Z):
    return np.maximum(Z, 0)

def ReLU_deriv(Z):
    return Z > 0


def forward_prop(W1, b1, W2, b2, W3, b3, X):
            Z1 = W1.dot(X) + b1
            A1 = ReLU(Z1)
            Z2 = W2.dot(A1) + b2
            A2 = ReLU(Z2)
            Z3 = W3.dot(A2) + b3
            A3 = Z3
            return Z1, A1, Z2, A2, Z3, A3

def backward_prop(Z1, A1, Z2, A2, W1, W2, W3, A3, Z3, X, Y):
            one_hot_Y = Y
            dZ3 = A3 - one_hot_Y
            dW3 = dZ3.dot(A2.T)
            db3 =  np.sum(dZ3,axis=1,keepdims=True)
            dZ2 = W3.T.dot(dZ3) * ReLU_deriv(Z2)
            dW2 = dZ2.dot(A1.T)
            db2 = np.sum(dZ2,axis=1,keepdims=True)
            dZ1 = W2.T.dot(dZ2) * ReLU_deriv(Z1)
            dW1 = dZ1.dot(X.T)
            db1 = np.sum(dZ1,axis=1,keepdims=True)
            return dW1, db1, dW2, db2, dW3, db3

def update_params(W1, b1, W2, b2, dW1, db1, dW2, db2, dW3, db3, W3, b3, alpha):
            W1 = W1 - alpha * dW1
            b1 = b1 - alpha * db1    
            W2 = W2 - alpha * dW2  
            b2 = b2 - alpha * db2 
            W3 = W3 - alpha * dW3  
            b3 = b3 - alpha * db3     
            return W1, b1, W2, b2, W3, b3

def gradient_descent(X, Y, alpha, iterations):
            W1, b1, W2, b2, W3, b3 = init_params()
            for i in range(iterations):
                Z1, A1, Z2, A2, Z3, A3 = forward_prop(W1, b1, W2, b2, W3, b3, X)
                dW1, db1, dW2, db2, dW3, db3 = backward_prop(Z1, A1, Z2, A2, W1, W2, W3, A3, Z3, X, Y)
                W1, b1, W2, b2, W3, b3 = update_params(W1, b1, W2, b2, dW1, db1, dW2, db2, dW3, db3, W3, b3, alpha)
                if i % 10 == 0:
                    print("Iteration: ", i)
                    print(A3)
            return W1, b1, W2, b2, W3, b3

def make_predictions(X, W1, b1, W2, b2, W3, b3):
            _, _, _, _, _, A3 = forward_prop(W1, b1, W2, b2, W3, b3, X)
            return A3
def predict_price(prices):
    m = 10
    maxy=max(prices)
    for i in range(500):
        data = prices
        data = np.array(data)
  
        X_dev = data[1+i:10+i].reshape(9,1) / maxy
        data_train = data[0+i:10+i]
        Y_train = data_train[9].reshape(1,1)/maxy
        X_train = data_train[0:9].reshape(9,1)/maxy
        m_train = X_train.shape



        W1, b1, W2, b2, W3, b3 = gradient_descent(X_train, Y_train, 0.02, 50)


        dev_predictions = make_predictions(X_dev, W1, b1, W2, b2, W3, b3)
        prices.append(float(dev_predictions.item() * maxy))
    return prices[10 : len(prices)]
