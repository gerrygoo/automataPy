# from automata import Automata
# from pprint import pprint

# myNfa = Automata(sigma=[0, 1], q_0 = 0, F = [3])
# for i in range(4): myNfa.add_state(i)

# myNfa.add_transition(0, 0, 0)
# myNfa.add_transition(0, 1, 0)

# myNfa.add_transition(0, 0, 1)

# myNfa.add_transition(1, 0, 2)
# myNfa.add_transition(1, 1, 2)

# myNfa.add_transition(2, 0, 3)

# myNfa.add_transition(3, 0, 3)
# myNfa.add_transition(3, 1, 3)
# # pprint(myNfa.delta)
# pprint(myNfa.dfa_transform())

from automata import *
aut = Automaton.fromJFLAP('1.jff.in')
aut.toJFLAP('1.jff.out')