import pickle
import os

abs = os.path.dirname(__file__)

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


def process_data(df,columns_to_drop=pit_decision_drop_columns):
    df.drop(columns=columns_to_drop,inplace=True)
    df.drop(columns='pitting_next_lap',inplace=True)
    pipe = pickle.load(open(os.path.join(abs,'../pipeline_pit_decision.pkl'),'rb'))
    df_processed = pipe.transform(df)
    return df_processed

def initialize_model():
    pass

def compile_model():
    pass

def train_model():
    pass

def evaluate_model():
    pass



def load_model_compound() :
    #return pickle.load(open("model_compound.pkl","rb"))
    pass

def load_model_pit():
    return pickle.load(open(os.path.join(abs,'../model_pit_decision_rf.pkl'),'rb'))
