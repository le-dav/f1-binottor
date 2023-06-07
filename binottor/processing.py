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

def check_second_compound(laps):
    years = laps['Year'].unique()
    for year in years:
        year_df = laps.loc[laps.Year == year]
        locations = year_df['Location'].unique()
        for location in locations:
            loc_df = year_df.loc[(year_df.Location == location)]
            drivers = loc_df['DriverNumber'].unique()
            for driver in drivers:
                driver_df = loc_df.loc[(loc_df.DriverNumber == driver)]
                driver_df["prev_compound"]=driver_df["Compound"].shift(1)
                first_index = driver_df.index[0]
                for index, row in driver_df.iterrows():
                    if index-1>=first_index:
                        if laps.loc[index-1,"second_compound"]==True :
                            laps.loc[index,"second_compound"]=True
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

laps_df, weather_df, track_status_df = load_dataset()
new_laps = compound_cleaning(laps_df,TIRE_MATCH)

print(new_laps['Compound'].value_counts())
