def appointment_node(state) -> dict:
    return {
        "results": [{
            "agent": "appointment",
            "status": "ok",
            "data": f"Dummy appointment agent handled: {state['query']}"
        }]
    }
