import pandas as pd
import numpy as np
import pickle

from sklearn.ensemble import RandomForestClassifier



def get_model_pit_decision():
    model_pit_decision = RandomForestClassifier(max_depth=5,
                                                class_weight="balanced",
                                                n_estimators=150,
                                                min_samples_leaf=3,
                                                max_features=20)

    return model_pit_decision


def train_model_pit_decision(model, X_train, y_train):
    model.fit(X_train, y_train)

    return model


def predict_pit_decision(model, X_test):
    y_pred = model.predict(X_test)

    return y_pred


def evaluate_pit_decision_model(y_test, y_pred):
    predictions = list(y_pred)
    reality = y_test.to_list()
    tracker = 0
    ones_count = reality.count(1)

    for i in range(len(reality)):
        if reality[i] == 1:
            if predictions[i] == 1:
                tracker += 1
            elif i > 0 and predictions[i - 1] == 1:
                tracker += 1
            elif i < len(predictions) - 1 and predictions[i + 1] == 1:
                tracker += 1
    metric = tracker / ones_count
    print(f"Score: {round(metric * 100, 2)}%")

    return metric


def save_model_pit_decision(model, model_name):
    pickle.dump(model, open(f'{model_name}.pkl', 'wb'))


# def load_model_pit_decision():
#     loaded_model_pit_decision = pickle.load(open('model_pit_decision_rf.pkl', 'rb'))

#     return loaded_model_pit_decision
