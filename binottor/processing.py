import pandas as pd

def add_race_progress(df):
    # Create Total Laps column
    df["TotalLaps"] = 0
    # Group data to get lap number per year per race
    grouped_data = df.groupby(by = ["Year", "Location"], as_index=False)["LapNumber"].max().rename(columns={"LapNumber":"TotalLaps"})
    grouped_data["Year_Location"] = grouped_data["Year"].map(str) + grouped_data["Location"]
    # Group data to get same info as grouped_data
    df["Year_Location"] = df["Year"].map(str) + df["Location"]
    # Merge data
    final_df = df.merge(grouped_data, on="Year_Location")
    # Clean data frame
    final_df.drop(columns=["TotalLaps_x", "Year_Location", "Year_y", "Location_y"], inplace=True)
    return final_df
