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

TYRE_STRESS = {
    'Mexico City': 4,
    'Lusail': 1,
    'Shanghai': 2,
    'Mugello': 1,
    'Hockenheim': 3,
    'Jeddah': 3,
    'Imola': 3,
    'São Paulo': 3,
    'Montréal': 3,
    'Singapore': 4,
    'Marina Bay': 4,
    'Barcelona': 1,
    'Spain': 1,
    'Spa-Francorchamps': 1,
    'Spielberg': 3,
    'Melbourne': 3,
    'Budapest': 3,
    'Nürburgring': 3,
    'Suzuka': 1,
    'Austin': 1,
    'Zandvoort': 1,
    'Bahrain': 3,
    'Portimão': 2,
    'Sochi': 4,
    'Monza': 1,
    'Yas Marina': 3,
    'Monaco': 5,
    'Miami': 3,
    'Istanbul': 1,
    'Baku': 3,
    'Monte Carlo': 5,
    'Yas Island': 3,
    'Le Castellet': 2,
    'Sakhir': 3,
    'Silverstone': 1
}

NAME_MATCH = {
    'Mercedes':'Mercedes',
    'Red Bull Racing':'RedBull',
    'McLaren': 'McLaren',
    'Ferrari':'Ferrari',
    'Williams':'Williams',
    'Haas F1 Team':'Haas',
    'AlphaTauri':'AlphaTauri',
    'Alfa Romeo Racing':'AlfaRomeo',
    'Renault':'Alpine',
    'Aston Martin':'AstonMartin',
    'Alpine':'Alpine',
    'Racing Point':'AstonMartin',
    'Toro Rosso':'AlphaTauri',
    'Alfa Romeo':'AlfaRomeo',
    'Sauber':'AlfaRomeo',
    'Force India':'AstonMartin',
    'Red Bull':'RedBull'
}


def load_dataset():
    laps_df = pd.read_csv(os.path.join(abs,"../raw_data/laps.csv"))
    weather_df = pd.read_csv(os.path.join(abs,"../raw_data/weather.csv"))
    track_status_df = pd.read_csv(os.path.join(abs,"../raw_data/track_status.csv"))
    results_df = pd.read_csv(os.path.join(abs,"../raw_data/results.csv"))
    driver_results_df = pd.read_csv(os.path.join(abs,"../raw_data/driver_results.csv"))
    locations_df = pd.read_csv(os.path.join(abs,"../raw_data/locations.csv"))
    return laps_df, weather_df, track_status_df, results_df, driver_results_df, locations_df


# FILL & CLEANING FUNCTIONS

def fill_na(laps):
    '''
    Replace the NaN of the df with good values
    '''
    laps["Team"] = laps["Team"].fillna("Renault")
    laps["Driver"] = laps["Driver"].fillna("OCO")
    laps["IsPersonalBest"] = laps["IsPersonalBest"].fillna(False)
    laps["Position"] = laps["Position"].fillna(method = "ffill")
    return laps

def TeamNames_cleaning(laps,name_mapping):
    '''
    Changes the TeamNames with the good ones
    '''
    laps['Team']=laps['Team'].map(name_mapping)
    return laps

def Compound_cleaning(laps,tire_mapping,backfilling=3):
    '''
    Changes the coumpounds with the good ones
    '''
    laps['Compound']=laps['Compound'].map(tire_mapping)
    laps['Compound'].replace('UNKNOWN',None,inplace=True)
    laps['Compound'].fillna(method="bfill",limit=backfilling,inplace=True)
    return laps

def remove_NaN_Teams(results):
     """ Removes the laps with Team = NaN """
     teams = results['Team'].unique().tolist()[:-1]
     results = results[results['Team'].isin(teams)]
     return results

def replace_NaN_Drivers(driver_results):
    driver_results.loc[933,'Driver'] = 'OCO'
    driver_results.loc[1679,'Driver'] = 'MAZ'
    driver_results.loc[1759,'Driver'] = 'MSC'
    return driver_results


# FEATURE ENGINEERING FUNCTIONS

def get_last_team_ranking(laps,results,locations):
    '''
    Adds a column to the laps DataFrame with the information of the last TeamRanking before the race
    '''

    for index, row in laps.iterrows():
        year = row['Year']
        location = row['Location']
        team = row['Team']
        gp_number = np.where(locations[str(year)] == location)[0][0]

    #If it's the 1st race of the season, takes the final ranking of last season :
        if gp_number == 0 :
            condition = (results['Year'] == year-1)
            ranking = results[condition][['Team','Points']].groupby(['Team']).sum('Points').sort_values('Points',ascending=False).reset_index()
            ranking['LastTeamRanking'] = ranking['Points'].rank(ascending=False,method='max')
            laps.loc[index,'LastTeamRanking'] = ranking[(ranking['Team'] == team)]['LastTeamRanking'].values[0]

    #Else, takes the actual ranking of the current season :
        else :
            list_locations = results[results['Year']== year]['Location'].unique().tolist()
            condition = (results['Year'] == year) & (results['Location'].isin(list_locations[0:gp_number]))
            ranking = results[condition][['Team','Points']].groupby(['Team']).sum('Points').sort_values('Points',ascending=False).reset_index()
            ranking['LastTeamRanking'] = ranking['Points'].rank(ascending=False,method='max')
            laps.loc[index,'LastTeamRanking'] = ranking[(ranking['Team'] == team)]['LastTeamRanking'].values[0]

    return laps

def tire_degradation_offset(laps):
    pass

def context_features(laps,track):
    '''
    Assess if whether or not two different compounds have been used during each GP for each driver.
    Adds a new column to the DataFrame.
    '''
    # Loop over every year
    laps['second_compound']=False
    track.Time = pd.to_timedelta(track.Time)
    laps['status']=1
    #laps['status_list']=np.array()
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
                    curr_time = pd.to_timedelta(row['Time'])
                    start_time = pd.to_timedelta(row['LapStartTime'])
                    status_changes = track.loc[(track.Location==location) & (track.Year==year) & (track.Time <= curr_time) & (track.Time >= start_time)]
                    if not status_changes.empty:
                        last_event = status_changes['Status'].values[-1]
                        events = status_changes['Status'].unique()
                        laps.loc[index,"status_list"]=str(events)
                        if 4 in events:
                            # Safety Car starting
                            laps.loc[index,"status"]=2
                            if last_event==1:
                                laps.loc[index,"status"]=4
                        elif 6 in events:
                            # VSC starting
                            laps.loc[index,"status"]=5
                            if last_event==1:
                                laps.loc[index,"status"]=7
                        elif 7 in events:
                            # VSC ending
                            laps.loc[index,"status"]=7
                            if last_event==1:
                                laps.loc[index,"status"]=1
                        elif 5 in events:
                            # VSC ending
                            laps.loc[index,"status"]=8
                            if last_event==1:
                                laps.loc[index,"status"]=1
                        elif 8 in events:
                            # VSC ending
                            laps.loc[index,"status"]=8
                            if last_event==1:
                                laps.loc[index,"status"]=9
                        if last_event==1:# and len(events)==1:
                            #print(events)
                            #print("Hello")
                            if laps.loc[index-1,"status"] in [2,3]:
                                #print("Go")
                                laps.loc[index,"status"]=4
                            elif laps.loc[index-1,"status"] in [5,6]:
                                laps.loc[index,"status"]=7
                            elif laps.loc[index-1,"status"] == 8:
                                laps.loc[index,"status"]= 9
                    else:
                        if index-1>=first_index:
                            if laps.loc[index-1,"status"] in [2,3]:
                                laps.loc[index,"status"]=3
                            elif laps.loc[index-1,"status"] in [5,6]:
                                laps.loc[index,"status"]=6
                            elif laps.loc[index-1,"status"] ==8:
                                laps.loc[index,"status"]=8
                            elif laps.loc[index-1,"status"] in [4,7,9]:
                                laps.loc[index,"status"]=1
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
    laps['pitting_this_lap']=False

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

def get_tyre_stress_level(df, tyre_stress_mapping):
    df["TyreStressLevel"] = df["Location"].map(tyre_stress_mapping)
    return df


# MERGE FUNCTIONS

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
    weather.drop_duplicates(subset=['Time_min', 'Location', 'Year'], keep='last',inplace=True)
    # Merge on both the track, the year and the time
    laps_extended = laps.merge(weather,on=["Year","Location","Time_min"],how="left",suffixes=(None,"_w"))
    # Backfill with weather data from previous lap
    for column in weather.columns:
        laps_extended[column].fillna(method="bfill",limit=backfilling,inplace=True)
    return laps_extended


# DROP FUNCTIONS

def keep_top_drivers_per_race(laps,driver_results,n=10):

    for index, row in laps.iterrows():
        year = row['Year']
        location = row['Location']
        driver = row['Driver']

        conditions = (driver_results['Driver']==driver) & (driver_results['Year']==year) & (driver_results['Location']==location)
        if len(driver_results[conditions]['Position'])==0:
            print(f"{driver} {year} {location}")
        laps.loc[index,'Final_Position'] = driver_results[conditions]['Position'].values[0]

    laps = laps[laps['Final_Position']<=n]
    return laps

def sunny_races(laps):
    #Group data to get data per race
    laps['LocationYear'] = laps['Location'] + ' ' + laps['Year'].astype(str)
    #Group data for every race where 'Wet' and 'Intermediate' tyres were used
    races_to_remove = laps[laps['Compound'].isin(['INTERMEDIATE','WET'])]['LocationYear'].unique().tolist()

    #Clean dataframe
    laps = laps[~laps['LocationYear'].isin(races_to_remove)]
    return laps

def mask_race_percentage(df, percentage=0.1):
    df = df[df["RaceProgress"] > percentage]
    return df

def drop_useless_columns(df):
    df.drop(columns=['Unnamed: 0', 'Time', 'DriverNumber', 'LapTime',
       'Stint', 'PitOutTime', 'PitInTime', 'Sector1Time', 'Sector2Time',
       'Sector3Time', 'Sector1SessionTime', 'Sector2SessionTime',
       'Sector3SessionTime', 'SpeedI1', 'SpeedI2', 'SpeedFL', 'SpeedST',
       'LapStartTime', 'LapStartDate', 'Deleted',
       'DeletedReason', 'FastF1Generated', 'IsAccurate', 'TrackStatus'], inplace = True)
    return df

def drop_duplicates_rows(df):
    df.drop_duplicates(inplace=True)
    return df

def shift_data(laps):
    years = laps['Year'].unique()
    laps['pitting_next_lap']=False
    laps['next_compound']=laps['Compound']
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
                    driver_df['next_compound']=driver_df['Compound'].shift(-2,fill_value=np.nan)
                    driver_df['pitting_next_lap']=driver_df['pitting_this_lap'].shift(-1,fill_value=False)
                    driver_df['next_compound'].fillna(method="ffill",inplace=True)
                    # Loop over every lap
                    for index, row in driver_df.iterrows():
                        laps.loc[index,'next_compound'] = row['next_compound']
                        laps.loc[index,'pitting_next_lap'] = row['pitting_next_lap']
    return laps


def preproc_data():
    laps_df, weather_df, track_status_df, results_df, driver_results_df, locations_df = load_dataset()
    print('Start fill_na...')
    laps_df = fill_na(laps_df) #ok
    print('Start TeamNames cleaning for laps...')
    laps_df = TeamNames_cleaning(laps_df,NAME_MATCH) #ok
    print('Start Team Names cleaning for results..')
    results_df = TeamNames_cleaning(results_df,NAME_MATCH)
    print('Start Coumpound cleaning...')
    laps_df = Compound_cleaning(laps_df,TIRE_MATCH) #ok
    print('Start Remove nan teams...')
    results_df = remove_NaN_Teams(results_df) #ok
    print('Start Remove nan Drivers...')
    driver_results_df = replace_NaN_Drivers(driver_results_df)
    print('Start get_last_team_ranking...')
    laps_df = get_last_team_ranking(laps_df,results_df,locations_df) #ok
    print('Start context_features...')
    context_features(laps_df,track_status_df) #ok
    print('Start add_race_progress...')
    laps_df = add_race_progress(laps_df) #ok
    print('Start is_pitting...')
    laps_df = is_pitting_feature(laps_df) #ok
    print('Start check_competitors...')
    check_competitors(laps_df)
    print('Start get_tyre_stress...')
    laps_df = get_tyre_stress_level(laps_df,TYRE_STRESS) #ok
    print('Start merge_weather...')
    laps_df = merge_weather(laps_df,weather_df) #ok
    print('Start keep_top_drivers...')
    laps_df = keep_top_drivers_per_race(laps_df,driver_results_df)
    print('Start sunny_races...')
    laps_df = sunny_races(laps_df) #ok
    print('Start mask_race_percentage...')
    laps_df = mask_race_percentage(laps_df) #ok
    print('Start drop_useless_columns...')
    laps_df = drop_useless_columns(laps_df) #ok
    print('Start drop_duplicate_rows...')
    laps_df = drop_duplicates_rows(laps_df) #ok
    print('Start shift_data...')
    laps_df = shift_data(laps_df)

    laps_df.to_csv(os.path.join(abs,"../raw_data/clean_data.csv"))
    return laps_df, results_df, driver_results_df
