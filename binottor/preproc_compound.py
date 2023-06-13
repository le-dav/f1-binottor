import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, RobustScaler
from sklearn.compose import make_column_transformer
from sklearn.pipeline import make_pipeline
from keras.utils import to_categorical

def create_copies(df):
    laps_for_model = df.copy()
    return laps_for_model

def drop_columns(df):
    return df.drop(columns=["Unnamed: 0.1",
                   "Time",
                   "DriverNumber",
                   "LapTime",
                   "Stint",
                   "PitOutTime",
                   "PitInTime",
                   "Sector1Time",
                   "Sector2Time",
                   "Sector3Time",
                   "Sector1SessionTime",
                   "Sector2SessionTime",
                   "Sector3SessionTime",
                   "SpeedI1",
                   "SpeedI2",
                   "SpeedFL",
                   "SpeedST",
                   "LapStartTime",
                   "LapStartDate",
                   "TrackStatus",
                   "Deleted",
                   "DeletedReason",
                   "FastF1Generated",
                   "IsAccurate",
                   "status_list",
                   "TotalLaps",
                   "Time_min",
                   "Unnamed: 0",
                   "Time_w",
                   "AirTemp",
                   "Humidity",
                   "Pressure",
                   "Rainfall",
                   "WindDirection",
                   "WindSpeed",
                   "Final_Position",
                   "LocationYear",
                   "FreshTyre",
                   "pitting_this_lap"])

def split_data_by_year(df):
    train_df_shuffled = df[df['Year'] < 2022].sample(frac=1)
    val_df_shuffled = df[df['Year'] == 2022].sample(frac=1)
    test_df_shuffled = df[df['Year'] == 2023].sample(frac=1)

    y_train = train_df_shuffled['next_compound']
    y_val = val_df_shuffled['next_compound']
    y_test = test_df_shuffled['next_compound']

    X_train = train_df_shuffled.drop(columns=['next_compound'])
    X_val = val_df_shuffled.drop(columns=['next_compound'])
    X_test = test_df_shuffled.drop(columns=['next_compound'])
    return X_train, X_val, X_test, y_train, y_val, y_test

def encode_target(y_train, y_val, y_test):
    le = LabelEncoder()
    le.fit(y_train)
    y_train_le = le.transform(y_train)
    y_val_le = le.transform(y_val)
    y_test_le = le.transform(y_test)
    return y_train_le, y_val_le, y_test_le

def convert_to_categorical(y_train_le, y_val_le, y_test_le):
    num_classes = np.max(y_train_le) + 1
    y_train_cat = to_categorical(y_train_le, num_classes=num_classes, dtype='float32')
    y_val_cat = to_categorical(y_val_le, num_classes=num_classes, dtype='float32')
    y_test_cat = to_categorical(y_test_le, num_classes=num_classes, dtype='float32')
    return y_train_cat, y_val_cat, y_test_cat

def define_features():
    cat_features = ["Driver", "Team", "IsPersonalBest", "Location",
'second_compound', 'Compound', 'close_ahead', 'close_behind', 'is_pitting_ahead','is_pitting_behind']
    cat_features_preproc = make_pipeline(OneHotEncoder(sparse=False, handle_unknown="ignore"))
    num_features = ["LapNumber", "TyreLife", "Position", "TyreStressLevel", "RaceProgress", "Year", 'LastTeamRanking','status',
                'TrackTemp', 'pitting_next_lap']
    num_features_preproc = make_pipeline(RobustScaler())
    return cat_features, num_features, cat_features_preproc, num_features_preproc

def preprocess_features(cat_features, num_features, cat_features_preproc, num_features_preproc):
    preproc_baseline = make_column_transformer(
        (cat_features_preproc, cat_features),
        (num_features_preproc, num_features),
        remainder="passthrough"
    )
    return preproc_baseline

def preproc_baseline_fit(preproc_baseline, X_train, X_val, X_test):
    preproc_baseline.fit(X_train)
    X_train_preproc = preproc_baseline.transform(X_train)
    X_val_preproc = preproc_baseline.transform(X_val)
    X_test_preproc = preproc_baseline.transform(X_test)
    return X_train_preproc, X_val_preproc, X_test_preproc

def final_preproc_compound (laps):
    laps = laps.copy()
    laps = drop_columns(laps)
    print(laps.columns)
    X_train, X_val, X_test, y_train, y_val, y_test = split_data_by_year(laps)
    y_train_le, y_val_le, y_test_le = encode_target(y_train, y_val, y_test)
    y_train_cat, y_val_cat, y_test_cat = convert_to_categorical(y_train_le, y_val_le, y_test_le)
    cat_features, num_features, cat_features_preproc, num_features_preproc = define_features()
    preproc_baseline = preprocess_features(cat_features, num_features, cat_features_preproc, num_features_preproc)
    X_train_preproc, X_val_preproc, X_test_preproc = preproc_baseline_fit(preproc_baseline, X_train, X_val, X_test)

    return X_train_preproc, X_val_preproc, X_test_preproc, y_train_cat, y_val_cat, y_test_cat
