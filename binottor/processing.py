import pandas as pd
import os

abs = os.path.dirname(__file__)
data_repo = "raw_data/"

TIRE_MATCH = {
    'HYPERSOFT': 'SOFT',
    'ULTRASOFT': 'SOFT',
    'SUPERSOFT': 'SOFT',
    'SOFT': 'SOFT',
    'MEDIUM': 'MEDIUM',
    'HARD': 'HARD',
    'INTERMEDIATE': 'INTERMEDIATE',
    'WET': 'WET',
    'UNKNOWN': 'UNKNOWN'
}

def load_dataset():
    laps_df = pd.read_csv(os.path.join(abs,"../raw_data/laps.csv"))
    weather_df = pd.read_csv(os.path.join(abs,"../raw_data/weather.csv"))
    track_status_df = pd.read_csv(os.path.join(abs,"../raw_data/track_status.csv"))
    return laps_df, weather_df, track_status_df


def compound_recategorization(laps,tire_mapping):
    new_laps = laps.copy()
    new_laps['Compound']=laps['Compound'].map(tire_mapping)
    return new_laps

def compound_cleaning(laps,tire_mapping,backfilling=3):
    new_laps = laps.copy()
    new_laps = compound_recategorization(new_laps,tire_mapping)
    new_laps['Compound'].replace('UNKNOWN',None,inplace=True)
    new_laps['Compound'].fillna(method="bfill",limit=backfilling,inplace=True)
    return new_laps

def tire_degradation_offset(laps):
    pass

def check_second_compound():
    pass

laps_df, weather_df, track_status_df = load_dataset()
new_laps = compound_cleaning(laps_df,TIRE_MATCH)

print(new_laps['Compound'].value_counts())
