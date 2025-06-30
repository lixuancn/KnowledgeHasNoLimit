from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict

class State(TypedDict):
    ingredients: str
    ret: dict
def supermarket(state):
    print("supermarket", state)
    return {"ingredients": state["ingredients"], "ret": {"supermarket_ret": "{}买到了".format(state["ingredients"])}}

def recipe(state):
    print("recipe", state)
    state["ret"]["recipe_ret"] = "搜到了红烧{}的菜谱".format(state["ingredients"])
    return state

def cooking(state):
    print("cooking", state)
    state["ret"]["cooking_ret"] = "做了一道红烧{}".format(state["ingredients"])
    return state


if __name__ == "__main__":
    sg = StateGraph(dict)
    sg.add_node("supermarket", supermarket)
    sg.add_node("recipe", recipe)
    sg.add_node("cooking", cooking)

    sg.add_edge(START, "supermarket")
    sg.add_edge("supermarket", "recipe")
    sg.add_edge("recipe", "cooking")
    sg.add_edge("cooking", END)

    graph = sg.compile()
    ret = graph.invoke({"ingredients": "羊排"})

    print(ret)
    print(ret["ret"]["supermarket_ret"])
    print(ret["ret"]["recipe_ret"])
    print(ret["ret"]["cooking_ret"])

