from binottor.processing import preproc_data

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
model = None #TODO : change with the real model

# Allowing all middleware is optional, but good practice for dev purposes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


@app.get("/predict")
def predict(X_pred_prepoc):
    y_pred = model.predict(X_pred_prepoc)
    return y_pred
