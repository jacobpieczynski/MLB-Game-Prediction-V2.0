# To Train the model
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

# Load the CSV file into a DataFrame
#train_data = pd.read_csv('train.csv').drop(columns=['Date', 'Home', 'Visitor', 'GameID', 'Year', 'AVG', 'AVG_10d', 'SLG_10d', 'ERA_10d'], axis=1)
#test_data = pd.read_csv('test.csv').drop(columns=['Date', 'Home', 'Visitor', 'GameID', 'Year', 'AVG', 'AVG_10d', 'SLG_10d', 'ERA_10d'], axis=1)
train_data = pd.read_csv('train2.csv').drop(columns=['Date', 'Home', 'Visitor', 'GameID', 'Year', 'FIP_10d', 'ERA_10d', 'ISO', 'SP_FIP', 'H2H', 'SP_WHIP', 'ISO_10d', 'AVG', 'AVG_10d'], axis=1)
test_data = pd.read_csv('test2.csv').drop(columns=['Date', 'Home', 'Visitor', 'GameID', 'Year', 'FIP_10d', 'ERA_10d', 'ISO', 'SP_FIP', 'H2H', 'SP_WHIP', 'ISO_10d', 'AVG', 'AVG_10d'], axis=1)
correlation_matrix = train_data.corr()
target_correlation = correlation_matrix['HWin'].abs().sort_values(ascending=False)

print('Correlation with the target variable:')
print(target_correlation)
X_train = train_data.drop('HWin', axis=1)
y_train = train_data['HWin']
X_test = test_data.drop('HWin', axis=1)
y_test = test_data['HWin']


model_average, model_best, model_min, rf_model_average = 0, 0, 1, 0
rng = 1
for i in range(rng):
    #X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, random_state=i) #random_state=705

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    model = LogisticRegression(max_iter=2500, C=0.005)

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