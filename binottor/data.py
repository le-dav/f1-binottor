import pandas as pd
import fastf1
import datetime


def get_laps_CSV(years):
    """ This function downloads the laps of all the races of the years you entered
    The parameter 'years' must be a list of integers """

    df_laps = pd.DataFrame()

    for year in years :
        season = fastf1.get_event_schedule(year)
        locations = season['Location'].values.tolist()
        df_laps_per_locations = pd.DataFrame()

        if year != int(datetime.date.today().strftime("%Y")) :
            locations = locations
        else :
            next_gp = fastf1.get_events_remaining()['Location'].values.tolist()[0]
            locations = season['Location'].values.tolist()[0:locations.index(next_gp)]


        for location in locations :
            session = fastf1.get_session(year, location, 'R')
            session.load()
            session.laps['Location'] = location
            session.laps['Year'] = year
            df_laps_per_locations = pd.concat([df_laps_per_locations,session.laps],ignore_index=True)

        df_laps = pd.concat([df_laps,df_laps_per_locations],ignore_index=True)

    df_laps.to_csv('../raw_data/laps.csv')
    print (f'The file laps.csv has been successfully downloaded for the following years : {years} ')

def get_trackstatus_CSV(years):
    """ This function downloads the track_status of all the races of the years you entered
    The parameter 'years' must be a list of integers """

    df_track_status = pd.DataFrame()

    for year in years :
        season = fastf1.get_event_schedule(year)
        locations = season['Location'].values.tolist()
        df_track_status_per_locations = pd.DataFrame()

        if year != int(datetime.date.today().strftime("%Y")) :
            locations = locations
        else :
            next_gp = fastf1.get_events_remaining()['Location'].values.tolist()[0]
            locations = season['Location'].values.tolist()[0:locations.index(next_gp)]

        for location in locations :
            session = fastf1.get_session(year, location, 'R')
            session.load()
            session.track_status['Location'] = location
            session.track_status['Year'] = year
            df_track_status_per_locations = pd.concat([df_track_status_per_locations,session.track_status],ignore_index=True)

        df_track_status = pd.concat([df_track_status,df_track_status_per_locations],ignore_index=True)

    df_track_status.to_csv('../raw_data/track_status.csv')
    print (f'The file track_status.csv has been successfully downloaded for the following years : {years} ')

def get_weather_CSV(years):
    """ This function downloads the weather data of all the races of the years you entered
    The parameter 'years' must be a list of integers """

    df_weather = pd.DataFrame()

    for year in years :
        season = fastf1.get_event_schedule(year)
        locations = season['Location'].values.tolist()
        df_weather_per_locations = pd.DataFrame()

        if year != int(datetime.date.today().strftime("%Y")) :
            locations = locations
        else :
            next_gp = fastf1.get_events_remaining()['Location'].values.tolist()[0]
            locations = season['Location'].values.tolist()[0:locations.index(next_gp)]

        for location in locations :
            session = fastf1.get_session(year, location, 'R')
            session.load()
            session.weather_data['Location'] = location
            session.weather_data['Year'] = year
            df_weather_per_locations = pd.concat([df_weather_per_locations,session.weather_data],ignore_index=True)

        df_weather = pd.concat([df_weather,df_weather_per_locations],ignore_index=True)

    df_weather.to_csv('../raw_data/weather.csv')
    print (f'The file weather.csv has been successfully downloaded for the following years : {years} ')

def get_results_CSV(years):
    """ This function downloads the final result of all the races per team of the years you entered
    The parameter 'years' must be a list of integers """

    df_results = pd.DataFrame()

    for year in years :
        season = fastf1.get_event_schedule(year)
        locations = season['Location'].values.tolist()
        df_results_per_locations = pd.DataFrame()

        if year != int(datetime.date.today().strftime("%Y")) :
            locations = locations
        else :
            next_gp = fastf1.get_events_remaining()['Location'].values.tolist()[0]
            locations = season['Location'].values.tolist()[0:locations.index(next_gp)]

        for location in locations :
            session = fastf1.get_session(year, location, 'R')
            session.load()
            points_per_team = session.results[['TeamName','Points']].groupby('TeamName').sum('Points').sort_values('Points',ascending=False).reset_index()
            points_per_team['Ranking'] = points_per_team['Points'].rank(ascending=False,method='max')
            points_per_team['Year']= year
            points_per_team['Location'] = location
            df_results_per_locations = pd.concat([df_results_per_locations,points_per_team],ignore_index=True)
            print(f'Done for {location} & year {year} !')


        df_results = pd.concat([df_results,df_results_per_locations],ignore_index=True)


    df_results.to_csv('../raw_data/results.csv')
    print (f'The file results.csv has been successfully downloaded for the following years : {years} ')

def get_results_driver_CSV(years):
    """ This function downloads the final result of all the races per driver of the years you entered
    The parameter 'years' must be a list of integers """

    df_results = pd.DataFrame()

    for year in years :
        season = fastf1.get_event_schedule(year)
        locations = season['Location'].values.tolist()
        df_results_per_locations = pd.DataFrame()

        if year != int(datetime.date.today().strftime("%Y")) :
            locations = locations
        else :
            next_gp = fastf1.get_events_remaining()['Location'].values.tolist()[0]
            locations = season['Location'].values.tolist()[0:locations.index(next_gp)]

        for location in locations :
            session = fastf1.get_session(year, location, 'R')
            session.load()
            points_per_driver = session.results[['Abbreviation','Position']].reset_index()
            points_per_driver['Year']= year
            points_per_driver['Location'] = location
            df_results_per_locations = pd.concat([df_results_per_locations,points_per_driver],ignore_index=True)
            print(f'Done for {location} & year {year} !')

        df_results = pd.concat([df_results,df_results_per_locations],ignore_index=True)

    df_results.to_csv('../raw_data/driver_results2023.csv')
    print (f'The file driver_results.csv has been successfully downloaded for the following years : {years}')

def get_locations_CSV(years):
    """ This function downloads the list of all the races of the years you entered
    The parameter 'years' must be a list of integers """

    locations_per_year = {}

    for year in years :
        season = fastf1.get_event_schedule(year)
        locations = season['Location'].values.tolist()
        locations_per_year[year] = locations

    df_locations = pd.DataFrame.from_dict(locations_per_year,orient='index').transpose()

    df_locations.to_csv('../raw_data/locations.csv')
    print (f'The file locations.csv has been successfully downloaded for the following years : {years} ')

def get_all_CSV(years):
    pass
