import pandas as pd
import fastf1
import datetime


def get_laps_CSV(years):
    """ This function downloads the laps of all the races of the years you entered
    The parameter 'years' must be a list of integers """

    df_laps = pd.DataFrame()

    for year in years :
        season = fastf1.get_event_schedule(year)
        if year != int(datetime.date.today().strftime("%Y")) :
            locations = season['Location'].values.tolist()
        else :
            next_gp = fastf1.get_events_remaining()['Location'].values.tolist()[0]
            locations = season['Location'].values.tolist()[0:locations.index(next_gp)]
        df_laps_per_locations = pd.DataFrame()

        for location in locations :
            session = fastf1.get_session(year, location, 'R')
            session.load()
            session.laps['Location'] = location
            session.laps['Year'] = year
            df_laps_per_locations = pd.concat([df_laps_per_locations,session.laps],ignore_index=True)

        df_laps = pd.concat([df_laps,df_laps_per_locations],ignore_index=True)

    df_laps.to_csv('laps.csv')
    print (f'The file laps.csv has been successfully downloaded for the following years : {years} ')


def get_trackstatus_CSV(years):
    """ This function downloads the track_status of all the races of the years you entered
    The parameter 'years' must be a list of integers """

    df_track_status = pd.DataFrame()

    for year in years :
        season = fastf1.get_event_schedule(year)
        if year != int(datetime.date.today().strftime("%Y")) :
            locations = season['Location'].values.tolist()
        else :
            next_gp = fastf1.get_events_remaining()['Location'].values.tolist()[0]
            locations = season['Location'].values.tolist()[0:locations.index(next_gp)]
        df_track_status_per_locations = pd.DataFrame()

        for location in locations :
            session = fastf1.get_session(year, location, 'R')
            session.load()
            session.track_status['Location'] = location
            session.track_status['Year'] = year
            df_track_status_per_locations = pd.concat([df_track_status_per_locations,session.track_status],ignore_index=True)

        df_track_status = pd.concat([df_track_status,df_track_status_per_locations],ignore_index=True)

    df_track_status.to_csv('track_status.csv')
    print (f'The file track_status.csv has been successfully downloaded for the following years : {years} ')


#def get_weather_CSV():

def get_results_CSV(years):
    """ This function downloads the final result of all the races of the years you entered
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


    df_results.to_csv('results.csv')
    print (f'The file results.csv has been successfully downloaded for the following years : {years} ')

get_results_CSV([2017])
