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

def init_model_compound():

    model = models.Sequential()

    reg = regularizers.l1(0.001)

    model.add(layers.Dense(128, activation="relu", input_dim=169, kernel_regularizer=regularizers.l1(0.001)))
    model.add(layers.Dense(128, activation="relu", kernel_regularizer=reg))
    model.add(layers.Dense(64, activation="relu", kernel_regularizer=reg))
    model.add(layers.Dense(64, activation="relu", kernel_regularizer=reg))
    model.add(layers.Dense(32, activation="relu", kernel_regularizer=reg))
    model.add(layers.Dense(32, activation="relu", kernel_regularizer=reg))

    model.add(layers.Dense(3, activation="softmax"))

    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    return model

def compile_model_compound():
    """
    Compile the Neural Network
    """
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

    print("✅ Model compiled")

    return model

def train_model_compound():
    """
    Fit the model and return a tuple (fitted_model, history)
    """
    es = EarlyStopping(patience=20, restore_best_weights=True)

    history = model.fit(X_train_preproc, y_train_cat,
          batch_size=256, epochs=1500,
          validation_data=(X_val_preproc, y_val_cat),
          callbacks=[es])

    return model, history

def evaluate_model():
    """
    Evaluate trained model performance on the dataset
    """
    if model is None:
        print(f"\n❌ No model to evaluate")
        return None

    metrics = model.evaluate(X_test_preproc,y_test_cat)

    return metrics

def init_model_pit():
    pass
