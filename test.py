from automata import *

aut = Automaton.fromJFLAP('answ.jff').dfa_transform()
# aut = Automaton.fromJFLAP('1.jff.in')
# aut.toJFLAP('1.jff.out')
print(aut.toLatex())

# from automata import *

# aut = Automaton.fromJFLAP('simple.jff')
# new = aut.dfa_transform()
# new.toJFLAP('simple.jff.out')
# print(new.toLatex())
