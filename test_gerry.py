from automata import *

aut = Automaton.fromJFLAP('simple.jff')
new = aut.dfa_transform()
print()
print(new.states)
