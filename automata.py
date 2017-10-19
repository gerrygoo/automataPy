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

        def escape(st):
            st = str(st)
            st = re.sub(r'([\{\}])', r'\\\1', st)
            return re.sub(r'(?<=\w)(\d+)', r'_{\1}', st)

        result.write('\\begin{enumerate}\n')
        qst = ', '.join([escape(x.name) for x in self.states.values()])
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
                     escape(self.initial.name) + ' \\in Q$\n')
        fst = ', '.join([escape(s.name)
                         for s in self.states.values() if s.final])
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
            n = re.sub(r'\D+', '', a)
            return int(n) if n != '' else -1

        class nameSorter(object):

            def __init__(self, state):
                self.name = state.name
                self.c = self.name.count(',')
                self.n = number_on_string(self.name)

            def __lt__(self, other):
                if self.c == other.c:
                    if self.n == other.n:
                        return self.name < other.name
                    return self.n < other.n
                return self.c < other.c

        ordered_states = sorted(self.states.values(), key=nameSorter)

        for state in ordered_states:
            name = escape(state.name)
            columns = []
            for r in reads:
                if r in state.transitions:
                    if len(state.transitions[r]) > 1:
                        columns.append(
                            '\\{' + ', '.join([escape(x.name) for x in state.transitions[r]]) + '\\}')
                    else:
                        columns.append(escape(state.transitions[r][0].name))
                else:
                    columns.append('\\varnothing')
            clst = ' $ & $ '.join(columns)
            result.write(ident + '$ ' + name + ' $ & $ ' +
                         clst + ' $\\\\\n' + ident + '\\hline\n')
        ident = '  '
        result.write(ident + '\\end{tabular}\n')
        result.write('\\end{enumerate}')

        return result.getvalue()

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
        self.states[new_state.id] = new_state
        if new_state.initial:
            self.initial = new_state

    def add_transition(self, from_state, with_value, to_state):
        self.states[from_state].addTransition(with_value, to_state)

    def clean_states(self):
        valid_set = set()
        self.traverse(self.initial, valid_set)
        self.states = {x.id: x for x in valid_set}

    def traverse(self, node, nodes):
        for t in node.transitions.values():
            for child in t:
                if child in nodes:
                    continue
                nodes.add(child)
                self.traverse(child, nodes)

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

        for psetel in pset[1:]: # for every state in power set 
            new_state = new.states[ pset_to_id[psetel] ]
            
            addr_upper = {}     # 'add up' where original transitions would take you. just the key -> bunch of ids idc
            for original_id in psetel:
                original_state = self.states[original_id]

                for key in original_state.transitions: 

                    if key not in addr_upper:
                       addr_upper[key] = set(original_state.transitions[key])
                    else:
                        addr_upper[key] |= set(original_state.transitions[key])
            
            # havinng computed that 'addition' proceed to figure out what its corresponding power set tuple would be
            # and that tuple's corresponding new id is FOR EVERY TRANSITION
            # that is, for every key
            for key, value in zip(addr_upper.keys(), addr_upper.values()):
                corr_id = pset_to_id[tuple(value)]

                new_state.addTransition(
                    read = key,
                    to = new.states[corr_id] 
                )


        new.clean_states()
        return new
