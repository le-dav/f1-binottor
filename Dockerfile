FROM python:3.10.6-bullseye

WORKDIR /prod

COPY requirements_prod.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY binottor binottor
COPY model_pit_decision_rf.pkl model_pit_decision_rf.pkl
COPY pipeline_pit_decision.pkl pipeline_pit_decision.pkl
COPY raw_data/ raw_data/

COPY Makefile Makefile

CMD uvicorn binottor.api.fast:app --host 0.0.0.0 --port $PORT
