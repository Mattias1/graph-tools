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
            print('The unit tests have {} errors:'.format(len(self.errors)))
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

        # Test case 0 - Invalid leaf case (tspTable)
        S = gi.fromDegreesEndpoints([2, 1, 2], [])
        Xi = gi.graph.vertices[1]
        val = self.graphInteraction.tspTable(S, Xi)
        if val < sys.maxsize:
            self.error('DP test case 0 - val: {}'.format(val))

        # Test case 1 - Valid edge select case (edgeSelect)
        # Xi = gi.graph.vertices[0]
        # targetDegrees = [1, 2, 1]
        # edges = []
        # for v in Xi.vertices:
        #     for e in v.edges:
        #         if e.other(v) not in Xi.vertices:
        #             continue
        #         if v.vid < e.other(v).vid:
        #             edges.append(e)
        # edges.sort(key=lambda e: e.cost)
        # val = gi.tspEdgeSelect(sys.maxsize, 0, Xi, edges, targetDegrees, [])
        # if val != 2:
        #     self.error('DP test case 1 - val: {}'.format(val))

        # Test case 2 - Sorting tours
        vs = gi.graph.originalGraph.vertices
        edgeList = vs[1].edges + vs[3].edges
        val = gi.sortTour(edgeList, [], True)
        if not val or str(edgeList) not in ['[0-1, 1-2, 2-3, 0-3]', '[(0,1), (1,2), (2,3), (0,3)]']:
            self.error('DP test case 2 - edgeList: {}'.format(edgeList))

