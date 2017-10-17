from collections import defaultdict


class Automata:

    def __init__(self, Q=set(), sigma=set(), delta=defaultdict(lambda: None), q_0=None, F=set()):
        self.Q = Q
        self.sigma = sigma
        self.delta = delta
        self.q_0 = q_0
        self.F = F

    def add_state(self, new_state):
        # self.Q.add(new_state)
        self.delta[new_state] = defaultdict(lambda: None)

    def add_transition(self, from_state, with_value, to_state):
        self.delta[from_state][with_value] = to_state


class State:
    last_id = 0

    def __init__(self, name='', initial=False, final=False, id=-1):
        if id == -1:
            self.id = State.last_id
            State.last_id += 1
        else:
            self.id = id
        self.name = 'q{}'.format(self.id) if name == '' else name
        self.initial = initial
        self.final = final

    def __hash__(self):
        return self.id.__hash__()

    def __lt__(self, other):
        return self.id < other.id

    def __eq__(self, other):
        return self.id == other.id


class Transition:

    def __init__(self, from, to, read):
        self.from = from
        self.to = to
        self.read = read

    def __eq__(self, other):
        return self.from == other.from and self.to == other.to and self.read == other.read

    def __hash__(self):
        return hash((self.to+self.from+self.read))
