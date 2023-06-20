import pandas as pd
import pickle

from imblearn.combine import SMOTETomek

from sklearn.pipeline import make_pipeline
from sklearn.compose import make_column_transformer
from sklearn.preprocessing import OneHotEncoder, RobustScaler


pit_decision_drop_columns = ["Unnamed: 0.1",
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
                             "next_compound",
                             "FreshTyre",
                             "pitting_this_lap"]
cat_features_pit_decision = ["Driver",
                             "Compound",
                             "Team",
                             "Location",
                             "second_compound",
                             "TyreStressLevel",
                             "status",
                             "close_ahead",
                             "close_behind",
                             "is_pitting_ahead",
                             "is_pitting_behind",
                             "IsPersonalBest",
                             "Position",
                             "Year"]
num_features_pit_decision = ["LapNumber",
                             "TyreLife",
                             "LastTeamRanking",
                             "TrackTemp"]


def get_X_y_split(df, columns_to_drop = pit_decision_drop_columns):
    # Drop useless columns
    df.drop(columns=columns_to_drop, inplace = True)

    # Change y to 0 & 1
    df["pitting_next_lap"] = df["pitting_next_lap"].apply(lambda x: 1 if x == True else 0)

    # Train / Val / Test split
    train_df_shuffled = df[df["Year"] < 2022].sample(frac=1)
    val_df_shuffled = df[df["Year"] == 2022].sample(frac=1)
    test_df_shuffled = df[df["Year"] == 2023].sample(frac=1)

    # Set y_train / y_val / y_test
    y_train = train_df_shuffled["pitting_next_lap"]
    y_val = val_df_shuffled["pitting_next_lap"]
    y_test = test_df_shuffled["pitting_next_lap"]

    # Set X_train / X_val / X_test
    X_train = train_df_shuffled.drop(columns="pitting_next_lap")
    X_val = val_df_shuffled.drop(columns="pitting_next_lap")
    X_test = test_df_shuffled.drop(columns="pitting_next_lap")

    return X_train, X_val, X_test, y_train, y_val, y_test


def get_pipeline(cat_features = cat_features_pit_decision, num_features = num_features_pit_decision):
    # Set categoric & numeric features with associate pipeline
    cat_features = cat_features
    cat_features_preproc = make_pipeline(OneHotEncoder(sparse=False, handle_unknown="ignore"))
    num_features = num_features
    num_features_preproc = make_pipeline(RobustScaler())

    # Set pipeline
    preproc_pipeline = make_column_transformer((cat_features_preproc, cat_features),
                                               (num_features_preproc, num_features),
                                               remainder="passthrough")

    return preproc_pipeline


def get_several_X_transformed(pipeline, X_train, X_val, X_test):
    pipeline.fit(X_train)
    pickle.dump(pipeline, open('pipeline_pit_decision.pkl', 'wb'))
    X_train_preproc = pipeline.transform(X_train)
    X_test_preproc = pipeline.transform(X_test)
    X_val_preproc = pipeline.transform(X_val)

    return X_train_preproc, X_val_preproc, X_test_preproc


def resample_classes(X_train_preproc, y_train):
    smt = SMOTETomek(sampling_strategy=0.5)
    X_train_preproc_resamp, y_train_resamp = smt.fit_resample(X_train_preproc, y_train)

    return X_train_preproc_resamp, y_train_resamp


def global_preproc():
    laps = pd.read_csv("../raw_data/new_clean_data.csv")
    X_train, X_val, X_test, y_train, y_val, y_test = get_X_y_split(laps)
    preproc_pipeline = get_pipeline()
    X_train_preproc, X_test_preproc, X_val_preproc = get_several_X_transformed(preproc_pipeline, X_train, X_val, X_test)
    X_train_preproc_resamp, y_train_resamp = resample_classes(X_train_preproc, y_train)

    return X_train_preproc_resamp, X_val_preproc, X_test_preproc, y_train_resamp, y_val, y_test
