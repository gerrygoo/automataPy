from collections import defaultdict

class Automata:

    def __init__(self, Q=set(), sigma=set(), delta=defaultdict(lambda : None), q_0=None, F = set()):
        self.Q = Q
        self.sigma = sigma
        self.delta = delta
        self.q_0 = q_0
        self.F = F
        

    def add_state(self, new_state):
        # self.Q.add(new_state)
        self.delta[new_state] = defaultdict(lambda : None)
    
    def add_transition(self, from_state, with_value, to_state):
        self.delta[from_state][with_value] = to_state 
