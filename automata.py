from collections import defaultdict

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

    def __init__(self, _from, to, read):
        self._from = _from
        self.to = to
        self.read = read

    def __eq__(self, other):
        return self._from == other._from and self.to == other.to and self.read == other.read

    def __hash__(self):
        return hash((self.to+self._from+self.read))


class Automata:

    def __init__(self, Q=[], sigma=[], delta={}, q_0=None, F = []):
        self.Q = set(Q)
        self.sigma = set(sigma)
        self.delta = defaultdict(None, delta)
        self.q_0 = q_0
        self.F = set(F)
        

    def add_state(self, new_state):
        self.Q.add(new_state)
        self.delta[new_state] = defaultdict(set)
    
    def add_transition(self, from_state, with_value, to_state):
            self.delta[from_state][with_value].add(to_state)

    def dfa_transform(self):
        def p(s):
            result = [[]]
            for elem in s:
                result.extend([x + [elem] for x in result])
            return result

        deterministic = {
            'Q':p(self.Q), 
            'sigma':self.sigma,
            'delta':None,
            'q_0':self.q_0,
            'F':None
        }

        # determinisic sigma
        delta = {} #from state in P(Q):list to set of states given a key
        # delta[from_tuple][key] = to_set

        for state_list in deterministic['Q'][1:]: 
            delta[tuple(state_list)] = {}

            for key in self.sigma:
                to_set = set()

                for ind_state in state_list:
                    to_set |= self.delta[ind_state][key]

                delta[tuple(state_list)][key] = to_set
            

        deterministic['delta'] = delta

        # deterministic F
        F = []
        for state_list in deterministic['Q']: 
            for ac in self.F:
                if ac in state_list:
                    F.append(state_list)
                    break
                
        deterministic['F'] = F
        return deterministic


    
