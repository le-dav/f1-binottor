import pandas as pd
import os
from binottor.processing import preproc_data
from binottor.model import load_model_compound, load_model_pit, process_data

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

abs = os.path.dirname(__file__)
data_repo = "api/"

app = FastAPI()
app.state.model_pit = load_model_pit()
app.state.model_compound = load_model_compound()

drivers_name = {
    'Pierre Gasly': 'GAS',
    'Sergio Perez': 'PER',
    'Fernando Alonso': 'ALO',
    'Charles Leclerc': 'LEC',
    'Lance Stroll': 'STR',
    'Lando Norris': 'NOR',
    'Kevin Magnussen': 'MAG',
    'Nico Hulkenberg': 'HUL',
    'Brendon Hartley': 'HAR',
    'Daniel Ricciardo': 'RIC',
    'Esteban Ocon': 'OCO',
    'Max Verstappen': 'VER',
    'George Russell': 'RUS',
    'Lewis Hamilton': 'HAM',
    'Sebastian Vettel': 'VET',
    'Carlos Sainz Jr.': 'SAI',
    'Kimi Räikkönen': 'RAI',
    'Valtteri Bottas': 'BOT',
    'Romain Grosjean': 'GRO',
    'Marcus Ericsson': 'ERI',
    'Alex Albon': 'ALB',
    'Daniil Kvyat': 'KVY',
    'Nobuharu Matsushita': 'MAT',
    'Artem Markelov': 'MAR',
    'Robert Kubica': 'KUB',
    'Antonio Giovinazzi': 'GIO',
    'Nyck de Vries': 'DEV',
    'Roy Nissany': 'NIS',
    'Marino Sato': 'SAT',
    'Mick Schumacher': 'MSC',
    'Nikita Mazepin': 'MAZ',
    'Guanyu Zhou': 'ZHO',
    'Ralph Boschung': 'BOS',
    'Jüri Vips': 'VIP',
    'Richard Verschoor': 'VER'
}


# Allowing all middleware is optional, but good practice for dev purposes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


# /predict_pit?driver=GAS&gp=Melbourne&year=2023
@app.get("/predict_pit")
def predict_pit(driver='Pierre Gasly', gp='Melbourne', year=2023):
    driver = drivers_name[driver]
    laps = pd.read_csv(os.path.join(abs,'../../raw_data/new_clean_data.csv'))
    X_pred = laps[(laps['Driver']==driver) & (laps['Location']==gp) & (laps['Year']==year)]
    X_pred_prepoc = process_data(X_pred)
    model = app.state.model_pit
    y_pred = model.predict(X_pred_prepoc)
    return dict(result = y_pred)

#@app.get("/predict_compound")
#def predict_compound(X_pred_prepoc_resamp):
    #model = app.state.model_compound
    #y_pred = model.predict(X_pred_prepoc_resamp)
    #return y_pred

@app.get('/')
def main():
    return {'coucou':'coucou'}

if __name__ == '__main__':
    pass
