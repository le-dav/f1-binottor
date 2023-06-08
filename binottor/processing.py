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
    'Renault':'Alphine',
    'Aston Martin':'AstonMartin',
    'Alpine':'Alpine',
    'Racing Point':'AstonMartin',
    'Toro Rosso':'AlphaTauri',
    'Alfa Romeo':'AlfaRomeo',
    'Sauber':'AlfaRomeo',
    'Force India':'AstonMartin',
    'Red Bull':'RedBull'
}


def change_TeamNames(laps,name_mapping):
    """ Changes the TeamNames with the good Names """

    laps['Team']=laps['Team'].map(name_mapping)
    return laps

def remove_NaN_Drivers(laps):
    """ Removes the laps with Team = NaN and Driver = NaN """

    teams = laps['Team'].unique().tolist()[:-1]
    laps = laps[laps['Team'].isin(teams)]
    return laps


def get_last_team_ranking(laps,results,locations):
    """ Adds a column to the laps DataFrame with the information of the last TeamRanking before the race """

    for index, row in laps.iterrows():

    #Infos Grand Prix
        year = row['Year']
        location = row['Location']
        team = row['Team']
        gp_number = np.where(locations[str(year)] == location)[0][0]

    #Si c'est le 1er Grand Prix de l'année - on récupère le classement final de la saison précédente :
        if gp_number == 0 :
            condition = (results['Year'] == year-1)
            ranking = results[condition][['Team','Points']].groupby(['Team']).sum('Points').sort_values('Points',ascending=False).reset_index()
            ranking['LastTeamRanking'] = ranking['Points'].rank(ascending=False,method='max')
            laps.loc[index,'LastTeamRanking'] = ranking[(ranking['Team'] == team)]['LastTeamRanking'].values[0]


    #Sinon, classement après le dernier Grand Prix
        else :
            list_locations = results[results['Year']== year]['Location'].unique().tolist()
            condition = (results['Year'] == year) & (results['Location'].isin(list_locations[0:gp_number]))
            ranking = results[condition][['Team','Points']].groupby(['Team']).sum('Points').sort_values('Points',ascending=False).reset_index()
            ranking['LastTeamRanking'] = ranking['Points'].rank(ascending=False,method='max')
            laps.loc[index,'LastTeamRanking'] = ranking[(ranking['Team'] == team)]['LastTeamRanking'].values[0]

    return laps

def keep_top_drivers_per_race(laps,driver_results,n=10):

    for index, row in laps.iterrows():

    #Infos Grand Prix & Pilote
        year = row['Year']
        location = row['Location']
        driver = row['Driver']

        conditions = (driver_results['Driver']==driver) & (driver_results['Year']==year) & (driver_results['Location']==location)
        laps.loc[index,'Final_Position'] = driver_results[conditions]['Position'].values[0]

    laps = laps[laps['Final_Position']<=n]
    return laps

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
  
def mask_race_percentage(df, percentage):
    df = df[df["RaceProgress"] > percentage]
    return df

def get_tyre_stress_level(df, tyre_stress_mapping):
    df["TyreStressLevel"] = df["Location"].map(tyre_stress_mapping)

  def sunny_races(df):
    #Group data to get data per race
    df['LocationYear'] = df['Location'] + ' ' + df['Year'].astype(str)
    #Group data for every race where 'Wet' and 'Intermediate' tyres were used
    df = df[(df['Compound'] == 'INTERMEDIATE') | (df['Compound'] == 'WET')]['LocationYear'].unique()
    #Clean dataframe
    df = df['LocationYear'].isin(df)
    df = df[~df]
    return df
