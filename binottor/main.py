#from processing import preproc_data
#from model import

#def main():
    #data = preproc_data()
    #model =
    #train =
    #evaluate =
    #predict =

import pandas as pd
# import model_compound

# from preproc_compound import final_preproc_compound
from preproc_pit_decision import global_preproc, pit_decision_drop_columns
from model_pit_decision import *



# def train_model_compound():
#     X_train_preproc, X_val_preproc, X_test_preproc, y_train_cat, y_val_cat, y_test_cat = final_preproc_compound(pd.read_csv('/Users/rosemansion/code/f1-binottor/raw_data/new_clean_data.csv'))
#     model_tire = model_compound.init_model_compound()
#     history = model_compound.train_model(model_tire, X_train_preproc, y_train_cat, X_val_preproc, y_val_cat)
#     metrics = model_compound.evaluate_model(model_tire, X_test_preproc, y_test_cat)
#     predict = model_compound.predict_model(model_tire, X_test_preproc,y_test_cat, history)
#     return history, metrics, predict


def main_model_pit_decision():
    X_train_preproc_resamp, X_val_preproc, X_test_preproc, y_train_resamp, y_val, y_test = global_preproc()
    model = get_model_pit_decision()
    trained_model = train_model_pit_decision(model, X_train_preproc_resamp, y_train_resamp)
    saved_model_pit_decision = save_model_pit_decision(trained_model)
    y_pred = predict_pit_decision(trained_model, X_test_preproc)
    metric = evaluate_model_pit_decision(y_test, y_pred)
    print(f"Model has been trained with a {round(metric * 100, 2)}% score and is now saved")


def predict_model_pit_decision(X_new):
    X_new.drop(columns=pit_decision_drop_columns, inplace = True)
    pipeline = pickle.load(open('pipeline_pit_decision.pkl', 'rb'))
    X_new_preproc = pipeline.transform(X_new)
    loaded_model_pit_decision = pickle.load(open('model_pit_decision_trained.pkl', 'rb'))
    y_pred = loaded_model_pit_decision.predict(X_new_preproc)
    return y_pred
