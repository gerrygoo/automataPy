from collections import defaultdict
from pprint import pprint
import xml.etree.ElementTree as ET
from itertools import chain, combinations

class Automata:

    def __init__(self, Q=None, sigma=None, delta=None, q_0=None, F = None):
        self.Q = set() if Q == None else Q
        self.sigma = set() if sigma == None else sigma
        self.delta = defaultdict(lambda : None) if sigma == None else delta
        self.q_0 = q_0
        self.F = set() if F == None else F

    def add_state(self, new_state):
        self.Q.add(new_state)
        self.delta[new_state] = defaultdict(set)

    def delete_state(self, rem_state):
        self.Q.remove(rem_state)
        self.delta.pop(rem_state,None)
    
    def add_transition(self, from_state, with_value, to_state):
        self.sigma.add(with_value)
        self.delta[from_state][with_value].add(to_state)

    def set_initial_state(self, state):
        self.Q.add(state)
        self.q_0 = state

    def add_final_state(self, state):
        self.Q.add(state)
        self.F.add(state)
    

    def to_JFlap(self, filename = 'output.jff'):
        struc = ET.Element('structure')
        document = ET.ElementTree(struc)
        ET.SubElement(struc, 'type').text = 'fa'
        autom = ET.SubElement(struc,'automaton')

        for state in sorted(self.Q):
            stateElem = ET.SubElement(autom, 'state')
            stateElem.set('id', state)
            stateElem.set('name', 'q'+state)

            ET.SubElement(stateElem,'x').text = '10.0'
            ET.SubElement(stateElem,'y').text = '10.0'
            
            if(state == self.q_0):
                ET.SubElement(stateElem,'initial')
            if(state in self.F):
                ET.SubElement(stateElem,'final')
        
        for state in self.Q:
            if(state in self.delta):
                for with_value in self.delta[state]:
                    if(self.delta[state][with_value]):
                        transElem = ET.SubElement(autom,'transition')
                        ET.SubElement(transElem,'from').text = state
                        ET.SubElement(transElem,'to').text = min(self.delta[state][with_value])
                        ET.SubElement(transElem,'read').text = with_value

        document.write(filename, xml_declaration=True,encoding='UTF-8')

    @staticmethod
    def from_JFlap(filename):

        autom = Automata()

        #parse the XML
        tree = ET.parse(filename)
        root = tree.getroot()
        
        for state in root.iter('state'):
            autom.add_state(state.get('id'))
            if(state.find('final') != None):
                autom.add_final_state(state.get('id'))
            if(state.find('initial') != None):
                autom.set_initial_state(state.get('id'))

        for transition in root.iter('transition'):
            autom.add_transition(transition.find('from').text,transition.find('read').text,transition.find('to').text)

        return autom

    def dfa_transform(self):
        def p(iterable):
            #powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
            s = list(iterable)
            c = chain.from_iterable(combinations(s, r) for r in range(len(s)+1))
            return [elem for elem in c]

        result = Automata()

        powerQ = p(self.Q)

        for i in range(len(powerQ)):
            powerQ[i] = tuple(sorted(powerQ[i]))
        
        indexes = {}
        isUsed = {}
        cont = 0
        for state in powerQ:
            indexes[state] = str(cont)
            isUsed[state] = False
            cont += 1

        isUsed[tuple(self.q_0)] = True

        for state in powerQ:
            result.add_state(indexes[state])
            for final_state in (self.F):
                if(final_state in state):
                    result.add_final_state(indexes[state])

        result.set_initial_state(indexes[(self.q_0,)])

        for state_tuple in powerQ:
            for with_value in self.sigma:
                result_set = set()
                for state in state_tuple:
                    result_set |= self.delta[state][with_value]
                result_tuple = tuple(sorted(result_set))
                isUsed[result_tuple] = True
                result.add_transition(indexes[state_tuple],with_value,indexes[result_tuple])
        
        for state_tuple in powerQ:
            if(not isUsed[state_tuple]):
                result.delete_state(indexes[state_tuple])
            
        """
        #debugging output delta
        print("<Delta>")
        for entry in result.delta:
            print(entry, dict(result.delta[entry]),sep=' -=- ')
        print("</Delta>")
        """
                
        return result

def main():
    a = Automata.from_JFlap('test_NFA.jff')
    res = a.dfa_transform()
    res.to_JFlap('NFAout.jff')
    
main()