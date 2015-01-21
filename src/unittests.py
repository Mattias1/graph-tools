import sys
from random import randrange

from .mainwin import *
from .graph import *
from .graph_interaction import *
from .settings import *
from .colors import *


class UnitTests():

    def __init__(self, mainWin):
        """Init runs unit tests"""
        self.graphInteraction = GraphInteraction(mainWin)
        self.graphInteraction.openFileWithPath("graph-unittests.txt")
        self.errors = []

        self.testToFromDegrees()
        self.testDPBaseCases()

        if (self.errors):
            print('\nThe unit tests have {} errors:'.format(len(self.errors)))
            print('-----------------------------------')
            for error in self.errors:
                print(error)
        print('Unit tests completed.\n');

    def error(self, description):
        self.errors.append(description)

    #
    # Actual unit tests
    #
    def testToFromDegrees(self):
        # Test if the toDegrees and fromDegreesEndpoints functions work properly
        tries = 99
        for i in range(tries):
            length = randrange(2, 20)
            degrees = [randrange(0, 3) for _ in range(length)]
            S = self.graphInteraction.fromDegreesEndpoints(degrees, [])
            result = self.graphInteraction.toDegrees(S)
            if result != degrees:
                self.error('To/from degrees - degrees: {}, S: {}, result degrees: {}'.format(degrees, S, result))

    def testDPBaseCases(self):
        # Test some base cases for tsp
        # def tspTable(self, S, Xi): -
        gi = self.graphInteraction
        gi.createRoot()

        # Test case 0 - Invalid case (tspTable)
        S = gi.fromDegreesEndpoints([2, 0, 2], [])
        Xi = gi.graph.vertices[1]
        val = self.graphInteraction.tspTable(S, Xi)
        if val < sys.maxsize:
            self.error('DP test case 0 - val: {}'.format(val))

        # Test case 1 - Valid leaf case (tspTable)
        S = gi.fromDegreesEndpoints([1, 2, 1], [2, 4])
        Xi = gi.graph.vertices[2]
        val = self.graphInteraction.tspTable(S, Xi)
        if val != 18:
            self.error('DP test case 1 - val: {}'.format(val))

        # Test case 2 - Valid case (tspTable)
        S = gi.fromDegreesEndpoints([1, 1, 2], [1, 4])
        Xi = gi.graph.vertices[1]
        val = self.graphInteraction.tspTable(S, Xi)
        if val != 38: # 19 + 11 + 8
            self.error('DP test case 2 - val: {}'.format(val))

        # Test case 3 - checking endpoints membership
        eps = [1, 2, 1, 5, 3, 4]
        if gi.inEndpoints(eps, 5, 3):
            self.error('Endpoints membership test case 3 - false positive')
        if not gi.inEndpoints(eps, 1, 5):
            self.error('Endpoints membership test case 3 - false negative')

