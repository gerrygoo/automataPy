from automata import *

aut = Automaton.fromJFLAP('answ.jff')
new = aut.dfa_transform()
new.toJFLAP('answ.jff.out')
# print(len(new.states))
# print(new.states)
print(new.toLatex())
