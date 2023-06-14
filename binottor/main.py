#from processing import preproc_data
#from model import

#def main():
    #data = preproc_data()
    #model =
    #train =
    #evaluate =
    #predict =
import model_compound
from preproc_compound import final_preproc_compound
import pandas as pd


def train_model_compound():
    X_train_preproc, X_val_preproc, X_test_preproc, y_train_cat, y_val_cat, y_test_cat = final_preproc_compound(pd.read_csv('/Users/rosemansion/code/f1-binottor/raw_data/new_clean_data.csv'))
    model_tire = model_compound.init_model_compound()
    history = model_compound.train_model(model_tire, X_train_preproc, y_train_cat, X_val_preproc, y_val_cat)
    metrics = model_compound.evaluate_model(model_tire, X_test_preproc, y_test_cat)
    predict = model_compound.predict_model(model_tire, X_test_preproc,y_test_cat, history)
    return history, metrics, predict

train_model_compound()
