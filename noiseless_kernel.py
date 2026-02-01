import bloqade.stim
import bloqade.tsim

import warnings

import cirq
import numpy as np
import matplotlib.pyplot as plt
import bloqade.cirq_utils as utils

from cirq.contrib.svg import SVGCircuit
from kirin.dialects.ilist import IList
from bloqade import squin, cirq_utils

warnings.filterwarnings("ignore")

@squin.kernel
def noiseless():
    q_data = squin.qalloc(7)
    # squin.u3(theta, phi, 0, q_data[6])

    # apply sqrt_y_adj to first 5 gates
    for i in range(6):
        squin.sqrt_y_adj(q_data[i])

    # apply cz to pairs
    squin.cz(q_data[1], q_data[2])
    squin.cz(q_data[3], q_data[4])
    squin.cz(q_data[5], q_data[6])

    # apply sqrt_y gate to injection state
    squin.sqrt_y(q_data[6])

    # apply cz to more pairs
    squin.cz(q_data[0], q_data[3])
    squin.cz(q_data[2], q_data[5])
    squin.cz(q_data[4], q_data[6])

    # apply sqrt_y gates
    for i in range(2, 7):
        squin.sqrt_y(q_data[i])

    # apply MORE cz gates
    squin.cz(q_data[0], q_data[1])
    squin.cz(q_data[2], q_data[3])
    squin.cz(q_data[4], q_data[5])

    squin.sqrt_y(q_data[1])
    squin.sqrt_y(q_data[2])
    squin.sqrt_y(q_data[4])

    """
    Encode aux |+>
    """
    q_aux_1 = squin.qalloc(7)
    squin.h(q_aux_1[6])

    # apply sqrt_y_adj to first 5 gates
    for i in range(6):
        squin.sqrt_y_adj(q_aux_1[i])

    # apply cz to pairs
    squin.cz(q_aux_1[1], q_aux_1[2])
    squin.cz(q_aux_1[3], q_aux_1[4])
    squin.cz(q_aux_1[5], q_aux_1[6])

    # apply sqrt_y gate to injection state
    squin.sqrt_y(q_aux_1[6])

    # apply cz to more pairs
    squin.cz(q_aux_1[0], q_aux_1[3])
    squin.cz(q_aux_1[2], q_aux_1[5])
    squin.cz(q_aux_1[4], q_aux_1[6])

    # apply sqrt_y gates
    for i in range(2, 7):
        squin.sqrt_y(q_aux_1[i])

    # apply MORE cz gates
    squin.cz(q_aux_1[0], q_aux_1[1])
    squin.cz(q_aux_1[2], q_aux_1[3])
    squin.cz(q_aux_1[4], q_aux_1[5])

    squin.sqrt_y(q_aux_1[1])
    squin.sqrt_y(q_aux_1[2])
    squin.sqrt_y(q_aux_1[4])


    """
    Encode aux |0>
    """
    q_aux_2 = squin.qalloc(7)

    # apply sqrt_y_adj to first 5 gates
    for i in range(6):
        squin.sqrt_y_adj(q_aux_2[i])

    # apply cz to pairs
    squin.cz(q_aux_2[1], q_aux_2[2])
    squin.cz(q_aux_2[3], q_aux_2[4])
    squin.cz(q_aux_2[5], q_aux_2[6])

    # apply sqrt_y gate to injection state
    squin.sqrt_y(q_aux_2[6])

    # apply cz to more pairs
    squin.cz(q_aux_2[0], q_aux_2[3])
    squin.cz(q_aux_2[2], q_aux_2[5])
    squin.cz(q_aux_2[4], q_aux_2[6])

    # apply sqrt_y gates
    for i in range(2, 7):
        squin.sqrt_y(q_aux_2[i])

    # apply MORE cz gates
    squin.cz(q_aux_2[0], q_aux_2[1])
    squin.cz(q_aux_2[2], q_aux_2[3])
    squin.cz(q_aux_2[4], q_aux_2[5])

    squin.sqrt_y(q_aux_2[1])
    squin.sqrt_y(q_aux_2[2])
    squin.sqrt_y(q_aux_2[4])

    for i in range(7):
        squin.cx(q_data[i], q_aux_1[i])

    squin.broadcast.measure(q_aux_1, key='result')

    for i in range(7):
        squin.cx(q_aux_2[i], q_data[i])
        squin.h(q_aux_2[i])

    squin.broadcast.measure(q_aux_2, key='result')
    squin.broadcast.measure(q_data, key='result')
