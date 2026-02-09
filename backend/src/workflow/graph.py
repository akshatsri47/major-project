from langgraph.graph import START,END,StateGraph
from ..agents.appointment import appointment_node
from ..state import RouterState
from .router import  classify_query,route_to_agent

Workflow = (
    StateGraph(RouterState)
    .add_node("classify",classify_query)
    .add_node("appointment",appointment_node)
    .add_edge(START,"classify")
    .add_conditional_edges(
        "classify",
        route_to_agent,
        ["appointment"]
    )
    .add_edge("appointment",END)
    .compile()

)
result = Workflow.invoke({
    "query": "is there any cardiologist avaliable",
    "user_id": None,
    "classifications": [],
    "results": [],
    "final_answer": ""
})
print(result)
