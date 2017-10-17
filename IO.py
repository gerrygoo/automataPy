#!/usr/bin/env python
from typing import *
import xmltodict
from automata import *


def readJFLAPFile(filename: str) -> Tuple[List[State], List[State]]:
    """
        Returns states, transitions
    """
    try:
        with open(filename) as file:
            jflapDict = xmltodict.parse(file.read())
            states = []
            for state in jflapDict['structure']['automaton']['state']:
                states.append(State(id=state['id'], name=state['name'],
                                    initial=('initial' in state), final=('final' in state)))
            transitions = []
            for trasition in jflapDict['structure']['automaton']['transition']:
                transitions.append(Transition(from=transition['from'], to=transition['to'],
                                              read=transition['read']))
            return states, transitions
    except OSError:
        print("The file: '{}' couln't be opened".format(filename))


def writeJFLAPFile(filename: str, states: Set, transitions: Set) -> None:
    jflapDict = {'structure': {'type': 'fa', 'automaton': {
        'state': states, 'transition': transitions}}}
    try:
        with open(filename, 'w') as file:
            file.write(xmltodict.unparse(jflapDict, pretty=True))
    except OSError:
        print("The file: '{}' couln't be opened or created".format(filename))
