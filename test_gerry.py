from automata import *

aut = Automaton.fromJFLAP('answ.jff')
new = aut.dfa_transform()
print(len(new.states))
print(new.states)
