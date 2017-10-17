from collections import defaultdict
import xml.etree.ElementTree as ET

class Automata:

    def __init__(self, Q=set(), sigma=set(), delta=defaultdict(lambda : None), q_0=None, F = set()):
        self.Q = Q
        self.sigma = sigma
        self.delta = delta
        self.q_0 = q_0
        self.F = F
        

    def add_state(self, new_state):
        self.Q.add(new_state)
        self.delta[new_state] = defaultdict(lambda : None)
    
    def add_transition(self, from_state, with_value, to_state):
        self.sigma.add(with_value)
        self.delta[from_state][with_value] = to_state 

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
                    transElem = ET.SubElement(autom,'transition')
                    ET.SubElement(transElem,'from').text = state
                    ET.SubElement(transElem,'to').text = self.delta[state][with_value]
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

def main():
    a = Automata.from_JFlap('tarea_5_DFA.jff')
    a.to_JFlap()
    
main()