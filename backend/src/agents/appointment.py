from langchain.agents import create_agent
from ..tools.appointment import get_availablity
from ..state import RouterState
from ..llm import get_model

model = get_model()

appointment_agent =  create_agent(
    model,
    tools = [get_availablity],
    system_prompt=(
    "You are an appointment agent which can answers questions about the doctors availability and can get their schedule their specailty and time"
    )
)
def appointment_node(state: RouterState):
    result = appointment_agent.invoke({
        "messages": [{"role": "user", "content": state["query"]}]
    })

    output = result["messages"][-1].content

    return {
        "results": [{
            "source": "appointment",
            "result": output
        }],
        "final_answer": output
    }
