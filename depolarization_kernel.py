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

"""
    DEPOLARIZATION noise affects physical qbits embedded in logical qbits

    LOCATION in circuit defined by NOISE_LOC parameter
    TYPE_INITIAL determines intial data's (always affected) number of affected qbits and type
    TYPE_OTHER determines halfway data's, aux_1's, aux_2's, etc number of affected qbits and type
    P=0.05 determines the strength of the noise. KEEP SMALL, definitely less than 10^-2

    NOISE_LOC values:
        1: initial data
        2: initial data and aux_1 after cx, before Z-basis measurement
        3: initial data and aux_2 after cx, before X-basis measurement

    TYPE_INITIAL, TYPE_OTHER values:
        1: 1 qbit noise
        2: 2 qbit noise
        3: 1 qbit noise acting in parallel on 2 qbits
"""

"""
    DEPOLARIZATION on 1 qbit in initial data
"""
@squin.kernel
def depolarize_1():
    P = 0.005
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

    squin.broadcast.depolarize(P, IList([q_data[0]]))

    for i in range(7):
        squin.cx(q_data[i], q_aux_1[i])

    squin.broadcast.measure(q_aux_1, key='result')

    for i in range(7):
        squin.cx(q_aux_2[i], q_data[i])
        squin.h(q_aux_2[i])

    squin.broadcast.measure(q_aux_2, key='result')
    squin.broadcast.measure(q_data, key='result')




"""
    DEPOLARIZATION on 1 qbit in initial data and 1 qbit in aux_1 after cx
"""
@squin.kernel
def depolarize_2():
    P = 0.005
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

    squin.broadcast.depolarize(P, IList([q_data[0]]))

    for i in range(7):
        squin.cx(q_data[i], q_aux_1[i])

    squin.broadcast.depolarize(P, IList([q_aux_1[0]]))

    squin.broadcast.measure(q_aux_1, key='result')

    for i in range(7):
        squin.cx(q_aux_2[i], q_data[i])
        squin.h(q_aux_2[i])

    squin.broadcast.measure(q_aux_2, key='result')
    squin.broadcast.measure(q_data, key='result')


"""
    DEPOLARIZATION on 1 qbit in initial data and 1 qbit in aux_2 after cx
"""
@squin.kernel
def depolarize_3():
    P = 0.005
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

    squin.broadcast.depolarize(P, IList([q_data[0]]))

    for i in range(7):
        squin.cx(q_data[i], q_aux_1[i])

    squin.broadcast.depolarize(P, IList([q_aux_1[0]]))

    squin.broadcast.measure(q_aux_1, key='result')

    for i in range(7):
        squin.cx(q_aux_2[i], q_data[i])

    squin.broadcast.depolarize(P, IList([q_aux_2[0]]))

    for i in range(7):
        squin.h(q_aux_2[i])

    squin.broadcast.measure(q_aux_2, key='result')
    squin.broadcast.measure(q_data, key='result')