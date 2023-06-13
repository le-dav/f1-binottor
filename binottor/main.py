#from processing import preproc_data
#from model import

#def main():
    #data = preproc_data()
    #model =
    #train =
    #evaluate =
    #predict =


from pkgutil import get_data
from .model import init_model_compound


def train_model_compound(model, X, y):
    history = model.fit()
    return history

def main():
    X, y = get_data()
    model = init_model_compound()
    train_model_compound(model, X, y)
