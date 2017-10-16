from collections import defaultdict

class Automata:

    def __init__(self, Q=[], sigma = None, delta=None, q_0=None, F = None):
        self.Q = set(Q)
        self.sigma = sigma
        self.delta = defaultdict(lambda : None) if not delta else delta
        self.q_0 = None if not q_0 else q_0
        self.F = F
        

    def add_state(self, new_state):
        self.Q.add(new_state)
        self.delta[new_state] = defaultdict(lambda : None)
    
    def add_transition(self, from_state, with_value, to_state):
        self.delta[from_state][with_value] = to_state 
