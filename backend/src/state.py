from typing_extensions  import Literal,TypedDict,Optional,Annotated
import operator

class AgentInput(TypedDict):
    query:str
    user_id:Optional[str]

class AgentOutput(TypedDict):
    source:str
    result:str

class Classification(TypedDict):
    source:Literal["billing","appointment","report"]
    query:str

class RouterState(TypedDict):
    query:str
    user_id:Optional[str]
    classifications:list[Classification]
    results:Annotated[list[AgentOutput],operator.add]
    final_answer:str

