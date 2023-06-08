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

laps_df, weather_df, track_status_df = load_dataset()
new_laps = compound_cleaning(laps_df,TIRE_MATCH)

print(new_laps['Compound'].value_counts())

def sunny_races(df):
    #Group data to get data per race
    df['LocationYear'] = df['Location'] + ' ' + df['Year'].astype(str)
    #Group data for every race where 'Wet' and 'Intermediate' tyres were used
    df = df[(df['Compound'] == 'INTERMEDIATE') | (df['Compound'] == 'WET')]['LocationYear'].unique()
    #Clean dataframe
    df = df['LocationYear'].isin(df)
    df = df[~df]
    return df


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
