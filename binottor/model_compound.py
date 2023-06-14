from plot_keras_history import plot_history
from tensorflow.keras import models, layers, regularizers
from tensorflow.keras.callbacks import EarlyStopping

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score, accuracy_score, precision_score
from sklearn.pipeline import make_pipeline
from sklearn.compose import make_column_transformer
from sklearn.preprocessing import OneHotEncoder, MinMaxScaler, RobustScaler, LabelEncoder
from tensorflow.keras.utils import to_categorical
from tensorflow.keras import models, layers, regularizers
from tensorflow.keras.callbacks import EarlyStopping

from preproc_compound import *

def init_model_compound():
    model = models.Sequential()

    reg = regularizers.l1(0.001)

    model.add(layers.Dense(128, activation="relu", input_dim=92, kernel_regularizer=regularizers.l1(0.001)))
    model.add(layers.Dense(128, activation="relu", kernel_regularizer=reg))
    model.add(layers.Dense(64, activation="relu", kernel_regularizer=reg))
    model.add(layers.Dense(64, activation="relu", kernel_regularizer=reg))
    model.add(layers.Dense(32, activation="relu", kernel_regularizer=reg))
    model.add(layers.Dense(32, activation="relu", kernel_regularizer=reg))

    model.add(layers.Dense(3, activation="softmax"))

    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

    return model

def train_model(model, X_train_preproc, y_train_cat, X_val_preproc, y_val_cat):
    es = EarlyStopping(patience=20, restore_best_weights=True)

    history = model.fit(X_train_preproc, y_train_cat,
          batch_size=256, epochs=1500,
          validation_data=(X_val_preproc, y_val_cat),
          callbacks=[es])

    return history

def evaluate_model(model, X_test_preproc, y_test_cat):
    metrics = model.evaluate(X_test_preproc, y_test_cat)
    return metrics

def predict_model(model, X_test_preproc, y_test_cat, history):
    y_classes = [np.argmax(y, axis=None, out=None) for y in y_test_cat]
    y_classes
    y_pred = model.predict(X_test_preproc)
    y_pred_encode = []
    for prediction in y_pred:
        y_pred_encode.append(prediction.argmax())

    baseline_acc = accuracy_score(y_classes, y_pred_encode)
    baseline_f1 = f1_score(y_classes, y_pred_encode, average='weighted')

    return baseline_acc, baseline_f1, plot_history(history)
