# To Train the model
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.feature_selection import RFE
from sklearn.preprocessing import StandardScaler

fieldnames = ['WinDiff', 'HomeAdv', 'WPctDiff', 'RunDiff', 'RPGDiff', 'RADiff', 'PythagDiff', 'Log5', 'PythagDiff_10d', 'Whisnant', 'OBP', 'SLG', 'AVG', 'ISO', 'OBP_10d', 'SLG_10d', 'AVG_10d', 'ISO_10d', 'SP_ERA', 'SP_WHIP', 'SP_FIP', 'ERA', 'WHIP', 'FIP', 'H2H', 'WHIP_10d', 'ERA_10d', 'FIP_10d', 'OPS', 'OPS_10d', 'SP_BB9', 'SP_HR9', 'SP_K9', 'BB9', 'K9', 'HR9', 'BB9_10d', 'K9_10d', 'HR9_10d']

# Load the CSV file into a DataFrame
#train_data = pd.read_csv('train.csv').drop(columns=['Date', 'Home', 'Visitor', 'GameID', 'Year', 'AVG', 'AVG_10d', 'SLG_10d', 'ERA_10d'], axis=1)
#test_data = pd.read_csv('test.csv').drop(columns=['Date', 'Home', 'Visitor', 'GameID', 'Year', 'AVG', 'AVG_10d', 'SLG_10d', 'ERA_10d'], axis=1)
train_data = pd.read_csv('train.csv').drop(columns=['Date', 'Home', 'Visitor', 'GameID', 'Year', 'HomeAdv', 'PythagDiff', 'Log5', 'PythagDiff_10d', 'SLG', 'OBP_10d', 'SLG_10d', 'AVG_10d', 'ISO_10d', 'SP_ERA', 'SP_WHIP', 'WHIP_10d', 'ERA_10d', 'FIP_10d', 'OPS_10d', 'K9_10d', 'HR9_10d'], axis=1)
test_data = pd.read_csv('test.csv').drop(columns=['Date', 'Home', 'Visitor', 'GameID', 'Year', 'HomeAdv', 'PythagDiff', 'Log5', 'PythagDiff_10d', 'SLG', 'OBP_10d', 'SLG_10d', 'AVG_10d', 'ISO_10d', 'SP_ERA', 'SP_WHIP', 'WHIP_10d', 'ERA_10d', 'FIP_10d', 'OPS_10d', 'K9_10d', 'HR9_10d'], axis=1)
#test_data = pd.read_csv('test.csv').drop(columns=['Date', 'Home', 'Visitor', 'GameID', 'Year'], axis=1)
#train_data = pd.read_csv('train.csv').drop(columns=['Date', 'Home', 'Visitor', 'GameID', 'Year'], axis=1)

#data = pd.read_csv('combined.csv').drop(columns=['Date', 'Home', 'Visitor', 'GameID', 'Year', 'HomeAdv', 'PythagDiff', 'Log5', 'PythagDiff_10d', 'SLG', 'OBP_10d', 'SLG_10d', 'AVG_10d', 'ISO_10d', 'SP_ERA', 'SP_WHIP', 'WHIP_10d', 'ERA_10d', 'FIP_10d', 'OPS_10d', 'K9_10d', 'HR9_10d'], axis=1)
correlation_matrix = train_data.corr()
target_correlation = correlation_matrix['HWin'].abs().sort_values(ascending=False)

print('Correlation with the target variable:')
print(target_correlation)
X_train = train_data.drop('HWin', axis=1)
y_train = train_data['HWin']
X_test = test_data.drop('HWin', axis=1)
y_test = test_data['HWin']
#X = data.drop('HWin', axis=1)
#y = data['HWin']


model_average, model_best, model_min, rf_model_average = 0, 0, 1, 0
rng = 1
#for i in range(len(fieldnames)):
for i in range(rng):
    #X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=705) #random_state=705

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    model = LogisticRegression(max_iter=2500, C=0.005)
    #model = RFE(mod, n_features_to_select=i+1, step=1, verbose=1)
    # 1: 57.0649 2: 56.970128 3: 56.80417
    #model = SVC(kernel='linear', gamma=10, C=1000)
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
    """
    print(model.support_)
    print("-----")
    print(model.ranking_)
    print(f'Columns: {X_train.columns}')
    exclude = []
    for j in range(len(model.ranking_)):
        if model.ranking_[j] == 1:
            #print(X_train.columns[i])
            pass
        else:
            exclude.append(X_train.columns[j])
    print('Fields toe exclude:', exclude)
    """
    print(f'TRIAL {i + 1} - LR Accuracy: {acc}')

model_average /= rng
rf_model_average /= rng

print(f'Best accuracy is {model_best}')
print(f'Min accuracy is {model_min}')
print(f'Accuracy range is {round(model_best - model_min, 8)}')
print(f'Overall accuracy Linear Regression is: {model_average}')