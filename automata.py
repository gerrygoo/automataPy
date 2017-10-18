import xmltodict
import re
from collections import Set


class State:
    last_id = 0

    def __init__(self, name=None, initial=False, final=False, id=-1, transitions=None):
        if id == -1:
            self.id = State.last_id
            State.last_id += 1
        else:
            self.id = int(id)
        self.name = 'q{}'.format(self.id) if name == None else name
        self.initial = initial
        self.final = final
        self.transitions = transitions if transitions != None else {}

    def addTransition(self, read, to):
        if read in self.transitions:
            self.transitions[read].append(to)
        else:
            self.transitions[read] = [to]

    def to_dict(self):
        res = {'@id': self.id, '@name': self.name}
        if self.initial:
            res['initial'] = None
        if self.final:
            res['final'] = None
        return res

    def transitionList(self):
        return [{'from': self.id, 'to': to.id, 'read': transition} for transition in self.transitions for to in self.transitions[transition]]

    def __hash__(self):
        return hash(self.id)

    def __lt__(self, other):
        return self.id < other.id

    def __eq__(self, other):
        if isinstance(other, int):
            return self.id == other
        return self.id == other.id

    def __str__(self):
        return "\nid: {}\nname:{}\ninitial: {}\nfinal: {}\ntransitions: [\n\t{}\n]".format(self.id, self.name, self.initial, self.final,
                                                                                           "\n\t".join(["read: {}, to: {}".format(x, ", ".join([str(k.id) for k in self.transitions[x]])) for x in self.transitions]))

    __repr__ = __str__


class Automaton:

    @staticmethod
    def fromJFLAP(filename):
        """
            Returns states, transitions
        """
        try:
            with open(filename) as file:
                jflapDict = xmltodict.parse(file.read())
                states = {}
                for state in jflapDict['structure']['automaton']['state']:
                    obj = State(id=state['@id'], name=state['@name'],
                                initial=('initial' in state), final=('final' in state))
                    states[obj.id] = obj
                for transition in jflapDict['structure']['automaton']['transition']:
                    id = int(transition['from'])
                    states[id].addTransition(
                        transition['read'], states[int(transition['to'])])
                return Automaton(states=states)
        except OSError:
            print("The file: '{}' couln't be opened".format(filename))

    def toJFLAP(self, filename):
        jflapDict = {'structure': {'type': 'fa', 'automaton': {
            'state': [state.to_dict() for state in self.states.values()],
            'transition': [transition for state in self.states.values() for transition in state.transitionList()]}}}
        try:
            with open(filename, 'w') as file:
                file.write(xmltodict.unparse(jflapDict, pretty=True))
        except OSError:
            print("The file: '{}' couln't be opened or created".format(filename))

    def toLatex(self):
        def underscore(st):
            return re.sub(r'(?<=\w)(\d+)', r'_{\1}', st)
        print('\\begin{enumerate}')
        stt = underscore(', '.join([str(x.name)
                                    for x in self.states.values()]))
        ident = '  '
        print(ident + '\\item $Q = \\{' + stt + '\\}$')
        reads = set()
        for st in self.states.values():
            for tt in st.transitions:
                reads.add(tt)
        reads = sorted(list(reads))
        stt = ", ".join([str(x) for x in reads])
        print(ident + '\\item $\\Sigma = \\{' + stt + '\\}$')
        print(ident + '\\item $q_0$ = $' +
              underscore(self.initial.name) + ' \\in Q$')
        print(ident + '\\item $F = \{' + ', '.join(
            [underscore(x.name) for x in self.states.values() if x.final]) + '\}$')
        print(ident + '\\item $\\delta \\colon Q \\times \\Sigma \\rightarrow Q = $')
        print(ident + '\\begin{tabular}{*{' + str(len(reads) + 1) + '}{c|}}')
        ident += '  '
        print(ident + '& $ ' +
              ' $ & $ '.join([str(x) for x in reads]) + ' $ \\\\')
        print(ident + '\\hline')
        ordered_states = []

        def number_on_string(a):
            n = re.sub(r'\D+', '', a.name)
            return int(n) if n != '' else 0

        if re.search(r'(\d+)', self.states[0].name):
            ordered_states = sorted(self.states.values(), key=number_on_string)
        elif self.states[0].name.strip()[0] == '{':
            ordered_states = sorted(
                self.states.values(), key=lambda a: a.name.count(','))
        else:
            ordered_states = sorted(self.states.values(), key=lambda a: a.name)
        # ya no jala
        for state in ordered_states:
            print(ident + '$ ' + underscore(state.name) + ' $ & $ ' + ' $ & $ '.join([underscore(
                state.transitions[x].name) if x in state.transitions else ' ' for x in reads]) + ' $\\\\\n' + ident + '\\hline')
        ident = '  '
        print(ident + '\\end{tabular}')
        print('\\end{enumerate}')

    def __init__(self, states=None, initial=None):
        self.states = states if states != None else {}
        if initial != None:
            self.initial = initial
        else:
            for st in self.states.values():
                if st.initial:
                    self.initial = st
                    break

    def add_state(self, new_state):
        self.states[new_state] = new_state
        if new_state.initial:
            self.initial = new_state

    def add_transition(self, from_state, with_value, to_state):
        self.states[from_state].addTransition(with_value, to_state)

        def dfa_transform(self):

        def p(s):
            result = [[]]
            for elem in s:
                result.extend([x + [elem] for x in result])
            return result

        def names(psetel):
            to_return = []
            for id in psetel:
                to_return.append(self.states[id].name)

            return to_return

        def is_initial(psetel):  # asumes there is only one and that it is len 1
            if len(psetel) == 1:
                return self.states[psetel[0]].initial
            return False

        def is_final(psetel):
            for id in psetel:
                if self.states[id].final:
                    return True
            return False

        new = self.__class__()

        pset = [tuple(i) for i in p(self.states)]
        pset_to_id = {}

        c = 0
        for psetel in pset[1:]:
            pset_to_id[psetel] = c
            new.add_state(
                State(
                    name="{" + ','.join(names(psetel)) + "}",
                    initial=is_initial(psetel),
                    final=is_final(psetel),
                    id=pset_to_id[psetel]
                )
            )

            c += 1

        for psetel in pset[1:]:
            new_state = new.states[pset_to_id[psetel]]

            for original_id in psetel:

                for key in self.states[original_id].transitions:

                    if key not in new_state.transitions:
                        new_state.transitions[key] = self.states[original_id].transitions[key]
                    else:
                        new_state.transitions[key] += self.states[original_id].transitions[key]

                    new_state.transitions[key] = list(
                        set(new_state.transitions[key]))

        return new
