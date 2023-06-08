import pandas as pd
import numpy as np
import os
from datetime import timedelta

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


def compound_cleaning(laps,tire_mapping,backfilling=3):
    laps['Compound']=laps['Compound'].map(tire_mapping)
    laps['Compound'].replace('UNKNOWN',None,inplace=True)
    laps['Compound'].fillna(method="bfill",limit=backfilling,inplace=True)
    return laps

def tire_degradation_offset(laps):
    pass

def check_second_compound(laps):
    '''
    Assess if whether or not two different compounds have been used during each GP for each driver.
    '''
    # Loop over every year
    years = laps['Year'].unique()
    for year in years:
        year_df = laps.loc[laps.Year == year]
        locations = year_df['Location'].unique()
        # Loop over every location
        for location in locations:
            loc_df = year_df.loc[(year_df.Location == location)]
            drivers = loc_df['DriverNumber'].unique()
            # Loop over every driver
            for driver in drivers:
                driver_df = loc_df.loc[(loc_df.DriverNumber == driver)]
                # Store in every lap the compound of the previous lap
                driver_df["prev_compound"]=driver_df["Compound"].shift(1)
                # Store the first index of the dataframe to avoid any out-of-bounds index
                first_index = driver_df.index[0]
                # Loop over every lap
                for index, row in driver_df.iterrows():
                    if index-1>=first_index:
                        # Switch to True if it was already True on the previous lap
                        if laps.loc[index-1,"second_compound"]==True :
                            laps.loc[index,"second_compound"]=True
                    # Switch to True if the Compound on this lap is different from the last lap
                    if laps.loc[index,"second_compound"]!=True:
                        if row["Compound"] != row["prev_compound"] and row["prev_compound"]:
                            laps.loc[index,"second_compound"]=True

def add_race_progress(df):
    # Group data to get lap number per year per race
    grouped_data = df.groupby(by = ["Year", "Location"], as_index=False)["LapNumber"].max().rename(columns={"LapNumber":"TotalLaps"})
    grouped_data["Year_Location"] = grouped_data["Year"].map(str) + grouped_data["Location"]
    # Group data to get same info as grouped_data
    df["Year_Location"] = df["Year"].map(str) + df["Location"]
    # Merge data
    df = df.merge(grouped_data, on="Year_Location")
    # Clean data frame
    df.drop(columns=["Year_Location", "Year_y", "Location_y"], inplace=True)
    df["RaceProgress"] = df["LapNumber"] / df["TotalLaps"]
    df.rename(columns={"Location_x": "Location", "Year_x": "Year"}, inplace=True)
    return df

def is_pitting_feature(laps):
    laps['pitting_this_lap'] = np.where(laps['PitInTime'].notna(), True, False)
    return laps

def check_competitors(laps, seconds_delta = 1, milliseconds_delta = 500):
    '''
    Calculate if whether or not competitors ahead and behind are inside a predefined gap from the car.
    '''
    close_timedelta = timedelta(seconds=seconds_delta,milliseconds=milliseconds_delta)
    laps['close_ahead']=False
    laps['close_behind']=False
    laps['is_pitting_ahead']=False
    laps['is_pitting_behind']=False

    # As we use itertuples instead of iterrows, create dict to match column names to tuple index.
    column_dict = { column: index+1 for index, column in enumerate(laps.columns)}

    # Looping on every individual lap
    for lap in laps.itertuples():
        position = lap[column_dict['Position']]
        track = lap[column_dict['Location']]
        year = lap[column_dict['Year']]
        lapnum = lap[column_dict['LapNumber']]
        # Store absolute time when the line was crossed for this lap.
        curr_time = pd.to_timedelta(lap[column_dict['Time']])
        position_ahead = position-1
        position_behind = position+1
        # If you're not the leader
        if position_ahead >= 1:
            ahead = laps.loc[(laps['Position']==position_ahead) & (laps['Location']==track) & (laps['Year']==year) & (laps['LapNumber']==lapnum)]
            ahead_pit = ahead.iloc[0]['pitting_this_lap']
            ahead_time = pd.to_timedelta(ahead.iloc[0]['Time'])
            delta_ahead = curr_time-ahead_time
            if delta_ahead>=close_timedelta:
                laps.loc[lap[0],"close_ahead"]=True
            laps.loc[lap[0],"is_pitting_ahead"]=ahead_pit
        # If you're not last
        if position_behind <=20:
            behind = laps.loc[(laps['Position']==position_behind) & (laps['Location']==track) & (laps['Year']==year) & (laps['LapNumber']==lapnum)]
            if len(behind)>0:
                behind_pit = behind.iloc[0]['pitting_this_lap']
                behind_time = pd.to_timedelta(behind.iloc[0]['Time'])
                delta_behind = behind_time-curr_time
                if delta_behind>=close_timedelta:
                    laps.loc[lap[0],"close_behind"]=True
                laps.loc[lap[0],"is_pitting_behind"]=behind_pit

def merge_weather(laps, weather,backfilling=6):
    '''
    Merge the laps dataframe with the weather dataframe.
    Caution: can backfill with inadequate data if the missing weather data is on the first lap. (0 case in our dataset)
    '''
    # Create a column with a minute-accurate timedelta object: will be the key for merging
    def add_standardized_time(df):
        df['Time_min']=pd.to_timedelta(df['Time'])
        df['Time_min']=df['Time_min'].values.astype('timedelta64[m]')
    add_standardized_time(laps)
    add_standardized_time(weather)
    # Merge on both the track, the year and the time
    laps_extended = laps.merge(weather,on=["Year","Location","Time_min"],how="left",suffixes=(None,"_w"))
    # Backfill with weather data from previous lap
    for column in weather.columns:
        laps_extended[column].fillna(method="bfill",limit=backfilling,inplace=True)
    return laps_extended

def merge_track_status():
    pass
