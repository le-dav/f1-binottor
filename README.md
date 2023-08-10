# F1-binottor
F1-Binottor is a Python project that aims to provide virtual strategy assistant related to Formula 1 (F1) racing.
This repository contains tools to retrieve and process F1 data, allowing users to explore various aspects of the sport and then predict during a race if the driver needs to pit or not and if we pit what type of compound do we need.

## Introduction
Formula 1 is a premier motorsport characterized by its cutting-edge technology, skilled drivers, and thrilling races.
F1-Binottor provides a range of tools to explore historical race data, driver statistics, team performances, and pitting predictions.

## Steps
Data Retrieval: Automatically fetches F1 data from FAST F1 API: https://docs.fastf1.dev/
Data Processing: Cleans and organizes the data for analysis.
Feature Engineering: Create new data on and off track.
Model for pitting: Random Forest.
Model for compounds: Dense Neural Network.

## Installation
After cloning the repository, to get started with F1-Binottor, follow these steps:

Create a virtual environment (recommended) and install dependencies:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
Start exploring F1 data using the provided Jupyter Notebooks.

## Data Sources
The F1 data used in this project is collected from reputable sources, ensuring accuracy and reliability. Data retrieval and preprocessing scripts can be found in the data directory.

## Model
We use two different models, the first one is a Random Forest for pit decision. Each lap we have a decision of pitting next lap or not.
Then if we are pitting we have a second model which is a deep learning model to choose the best compounds.


Feel free to explore the F1-Binottor repository to uncover valuable insights and analyses related to Formula 1 racing. If you have questions, suggestions, or feedback, don't hesitate to get in touch!
