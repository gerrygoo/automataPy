import xmltodict
import re
from collections import Set
from io import StringIO


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
        return "\nid: {}\nname:{}\ninitial: {}\nfinal: {}\ntransitions: [\n\t{}\n]".format(
            self.id,
            self.name,
            self.initial,
            self.final,
            "\n\t".join(
                [
                    "read: {}, to: {}".format(
                        x,
                        ", ".join([str(k.name) for k in self.transitions[x]])
                    ) for x in self.transitions]
            )
        )

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
        result = StringIO()

        def underscore(st):
            return re.sub(r'(?<=\w)(\d+)', r'_{\1}', st)

        def myJoin(st, col, val, isSet=False):
            if isSet:
                return st.join(['\\{' + val(x) + '\\}' for x in col])
            return st.join([val(x) for x in col])

        result.write('\\begin{enumerate}\n')
        qst = underscore(
            myJoin(', ', self.states.values(), lambda s: str(s.name), self.from_nfa))
        ident = '  '
        result.write(ident + '\\item $Q = \\{' + qst + '\\}$\n')
        reads = set()
        for st in self.states.values():
            for tt in st.transitions:
                reads.add(tt)
        reads = sorted(list(reads))
        stt = ", ".join([str(x) for x in reads])
        result.write(ident + '\\item $\\Sigma = \\{' + stt + '\\}$\n')
        result.write(ident + '\\item $q_0$ = $' +
                     underscore(self.initial.name) + ' \\in Q$\n')
        fst = myJoin(', ', [x for x in self.states.values() if x.final],
                     lambda s: underscore(s.name), self.from_nfa)
        result.write(ident + '\\item $F = \\{' + fst + '\\}$\n')
        result.write(
            ident + '\\item $\\delta \\colon Q \\times \\Sigma \\rightarrow Q = $\n')
        result.write(
            ident + '\\begin{tabular}{*{' + str(len(reads) + 1) + '}{c|}}\n')
        ident += '  '
        result.write(ident + '& $ ' +
                     ' $ & $ '.join([str(x) for x in reads]) + ' $ \\\\\n')
        result.write(ident + '\\hline\n')
        ordered_states = []

        def number_on_string(a):
            n = re.sub(r'\D+', '', a.name)
            return int(n) if n != '' else 0

        if self.from_nfa:
            ordered_states = sorted(
                self.states.values(), key=lambda a: a.name.count(','))
        elif re.search(r'(\d+)', self.states[0].name):
            ordered_states = sorted(self.states.values(), key=number_on_string)
        else:
            ordered_states = sorted(self.states.values(), key=lambda a: a.name)

        for state in ordered_states:
            name = underscore(state.name)
            columns = []
            for r in reads:
                if r in state.transitions:
                    if self.from_nfa:
                        columns.append(underscore(
                            '\\{' + myJoin(', ', state.transitions[r], lambda s: str(s.name)) + '\\}'))
                    else:
                        columns.append(underscore(
                            state.transitions[r][0].name))
                else:
                    columns.append('' if not self.from_nfa else '\\{\\}')
            if self.from_nfa:
                name = '\\{' + name + '\\}'
            clst = ' $ & $ '.join(columns)
            result.write(ident + '$ ' + name + ' $ & $ ' +
                         clst + ' $\\\\\n' + ident + '\\hline\n')
        ident = '  '
        result.write(ident + '\\end{tabular}\n')
        result.write('\\end{enumerate}')

        return result.getvalue()

    def __init__(self, states=None, initial=None, from_nfa=False):
        self.states = states if states != None else {}
        if initial != None:
            self.initial = initial
        else:
            for st in self.states.values():
                if st.initial:
                    self.initial = st
                    break
        self.from_nfa = from_nfa

    def add_state(self, new_state):
        self.states[new_state.id] = new_state
        if new_state.initial:
            self.initial = new_state

    def add_transition(self, from_state, with_value, to_state):
        self.states[from_state].addTransition(with_value, to_state)

    def clean_states(self):
        counts = {x: 0 for x in self.states.values()}
        for state in self.states.values():
            for tr in state.transitions.values():
                for to in tr:
                    counts[to] += 1
        self.states = {x.id: x for x in counts if counts[x] > 0 or x.initial}

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

        new = self.__class__(from_nfa=True)

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
                    key_map = {}

                    if key not in key_map:
                        key_map[key] = [
                            i.id for i in self.states[original_id].transitions[key]]
                    else:
                        key_map[key] += [i.id for i in self.states[original_id].transitions[key]]

                    # new_state.transitions[key] = list(set(new_state.transitions[key]))
                    key_map[key] = list(set(key_map[key]))

                    new_state.transitions[key] = [new.states[pset_to_id[tuple(
                        key_map[key])]]]
        new.clean_states()
        return new
