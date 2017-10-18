from automata import *

aut = Automaton.fromJFLAP('1.jff.in')
aut.toJFLAP('1.jff.out')
aut.toLatex()
