import pandas as pd

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

def mask_race_percentage(df, percentage):
    df = df[df["RaceProgress"] > percentage]
    return df

def get_tyre_stress_level(df):
    params = {'Mexico City': 4,
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
    'Silverstone': 1}
    df["TyreStressLevel"] = df["Location"].map(params)
    return df
