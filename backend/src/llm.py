from langchain import init_chat_model
from .config import Model_name

_model = None

def init_model():
    global_model
    if _model is None:
        _model = init_chat_model(Model_name)
    return _model
def get_model():
    return init_model()


