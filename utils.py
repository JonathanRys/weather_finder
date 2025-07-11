import json

def get_states():
    with open('states.json', 'r') as file:
        states = json.load(file)
    return states

