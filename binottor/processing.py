import numpy as np

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
    laps = laps[laps['Team'].isin(test)]
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
