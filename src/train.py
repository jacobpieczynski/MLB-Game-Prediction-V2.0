# To Train the model
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

# Load the CSV file into a DataFrame
data = pd.read_csv('stats.csv').drop(columns=['Date', 'Home', 'Visitor', 'GameID'], axis=1)
X = data.drop('HWin', axis=1)
y = data['HWin']

model_average, model_best, rf_model_average = 0, 0, 0
rng = 100
for i in range(rng):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1) #random_state=705
    #data = data[(np.abs(stats.zscore(data)) < 3).all(axis=1)] 

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    model = LogisticRegression()
    model.fit(X_train_scaled,y_train)
    y_pred = model.predict(X_test_scaled)

    def accuracy(y_pred, y_test):
        return np.sum(y_pred==y_test)/len(y_test)

    acc = accuracy(y_pred, y_test)
    model_average += acc
    if acc >= model_best:
        model_best = acc
    print(f"TRIAL {i} - LR Accuracy: {acc}")

model_average /= rng
rf_model_average /= rng

print(f"Best accuracy is {model_best}")
print(f"Overall accuracy Linear Regression is: {model_average}")