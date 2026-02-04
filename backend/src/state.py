from typing import literal,Typedict,Optional
import operator

class AgentInput(Typedict):
    query:str
    user_id:Optional[str]

class AgentOutput(Typedict):
    source:str,
    result:str

class Classification(Typedict):
    source:literal["billing","appointment","report"],
    query:str

class RouterState(Typedict):
    query:str,
    user_id:Optional[str]
    classifications:list[Classification]
    results:Annoated[list[AgentOutput],operator.add]
    final_answer:str

