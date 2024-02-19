# To Train the model
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

# Load the CSV file into a DataFrame
data = pd.read_csv('stats.csv').drop(columns=['Date', 'Home', 'Visitor', 'GameID'], axis=1)
correlation_matrix = data.corr()
target_correlation = correlation_matrix['HWin'].abs().sort_values(ascending=False)

print('Correlation with the target variable:')
print(target_correlation)
X = data.drop('HWin', axis=1)
y = data['HWin']

model_average, model_best, model_min, rf_model_average = 0, 0, 1, 0
rng = 100
for i in range(rng):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.15, random_state=i) #random_state=705

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    model = LogisticRegression()
    
    #model = RandomForestClassifier()
    model.fit(X_train_scaled,y_train)
    y_pred = model.predict(X_test_scaled)

    def accuracy(y_pred, y_test):
        return np.sum(y_pred==y_test)/len(y_test)

    acc = accuracy(y_pred, y_test)
    model_average += acc
    if acc >= model_best:
        model_best = acc
    elif acc <= model_min:
        model_min = acc
    print(f'TRIAL {i + 1} - LR Accuracy: {acc}')

model_average /= rng
rf_model_average /= rng

print(f'Best accuracy is {model_best}')
print(f'Min accuracy is {model_min}')
print(f'Accuracy range is {round(model_best - model_min, 8)}')
print(f'Overall accuracy Linear Regression is: {model_average}')