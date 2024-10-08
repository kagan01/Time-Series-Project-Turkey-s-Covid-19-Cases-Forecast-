# -*- coding: utf-8 -*-
"""LSTM.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1CKnBRZQjvpxIVXHBm9OquZfC9jW3oUGb
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df= pd.read_csv("data.csv",sep=";",index_col="Date",parse_dates=True)

df= df[["Case"]]

df["Case"]=df["Case"].diff()
df["Case"].fillna(1,inplace=True)
df["Case"]=df["Case"].astype(int)

df.head()

df.plot(figsize=(12,6))

from statsmodels.tsa.seasonal import seasonal_decompose

decomposition = seasonal_decompose(df['Case'], model='additive')

# Plot the decomposed components
decomposition.plot().suptitle('Time Series Decomposition of Case Data')

residuals = decomposition.resid.dropna()  # Removing NaN values which are a result of the decomposition
z_scores = np.abs((residuals - residuals.mean()) / residuals.std())

threshold = 3
anomalies = residuals[z_scores > threshold]

# Replace anomalies with the median value of 'Case'
median_value = df['Case'].median()
df.loc[anomalies.index, 'Case'] = median_value

df.plot(figsize=(12,6))

from statsmodels.tsa.seasonal import seasonal_decompose

results = seasonal_decompose(df['Case'])
results.plot();

len(df)

train= df.iloc[:805]
test= df.iloc[805:]

from sklearn.preprocessing import MinMaxScaler
scaler = MinMaxScaler()

df.head(),df.tail()

scaler.fit(train)
scaled_train = scaler.transform(train)
scaled_test = scaler.transform(test)

scaled_train[:10]

from keras.preprocessing.sequence import TimeseriesGenerator

n_input = 7
n_features = 1
generator = TimeseriesGenerator(scaled_train, scaled_train, length=n_input, batch_size=64)

X,y = generator[0]
print(f'Given the Array: \n{X.flatten()}')
print(f'Predict this y: \n {y}')

X.shape

test

from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM

model = Sequential()
model.add(LSTM(100, activation='relu', input_shape=(n_input, n_features)))
model.add(Dense(1))
model.compile(optimizer='adam', loss='mse')

model.summary()

model.fit(generator,epochs=30)

loss_per_epoch = model.history.history['loss']
plt.plot(range(len(loss_per_epoch)),loss_per_epoch)

last_train_batch = scaled_train[-7:]

last_train_batch = last_train_batch.reshape((1, n_input, n_features))

model.predict(last_train_batch)

scaled_test[0]

test_predictions = []

first_eval_batch = scaled_train[-n_input:]
current_batch = first_eval_batch.reshape((1, n_input, n_features))

for i in range(len(test)):

    # get the prediction value for the first batch
    current_pred = model.predict(current_batch)[0]

    # append the prediction into the array
    test_predictions.append(current_pred)

    # use the prediction to update the batch and remove the first value
    current_batch = np.append(current_batch[:,1:,:],[[current_pred]],axis=1)

test_predictions

test

true_predictions = scaler.inverse_transform(test_predictions)
print(true_predictions)

test['Predictions'] = true_predictions

test.plot(figsize=(14,5))
plt.ylim(500, 1400)
plt.grid()
plt.show()

from sklearn.metrics import mean_squared_error
from math import sqrt
rmse=sqrt(mean_squared_error(test['Case'],test['Predictions']))
print(rmse)

from sklearn.metrics import mean_absolute_error, mean_squared_error, mean_absolute_percentage_error

# Calculating MAE, MSE, and MAPE between case and pred columns
mae = mean_absolute_error(test['Case'],test['Predictions'])
mse = mean_squared_error(test['Case'],test['Predictions'])
mape = mean_absolute_percentage_error(test['Case'],test['Predictions'])

mae, mse, mape