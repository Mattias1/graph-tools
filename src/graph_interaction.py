import sys
from .settings import *
from .graph import *
from contextlib import suppress


class GraphInteraction():
    def __init__(self, mainWin):
        self.initKeymap()
        self.graph = TreeDecomposition(Graph(True))
        self.hoverVertex = None
        self.hoverEdge = None
        self.selectedVertices = [] # List with vertex ids
        self.mainWin = mainWin
        self.isTreeDecomposition = type(self.graph) == TreeDecomposition

    def redraw(self):
        self.mainWin.redraw()

    def initKeymap(self):
        self.keymap = {
            'LMB': self.selectVertex,
            'RMB': self.selectVertex,
            'a': self.selectAll,
            'Esc': self.deselect,
            'v': self.addVertex,
            'b': self.addBag,
            'd': self.removeVertices,
            'c': self.cliqueify,
            'p': self.pathify,
            't': self.treeify,
            '1': self.toggleDrawText,
            'q': self.tspDP,
            'Ctrl-s': self.saveAs,
            'Ctrl-o': self.openFile,
            'Ctrl-c': self.quit
        }

    #
    # Graph editing tools
    #
    def selectVertex(self):
        """(De)select a vertex"""
        if not self.hoverVertex:
            return False
        if self.hoverVertex in self.selectedVertices:
            with suppress(ValueError):
                self.selectedVertices.remove(self.hoverVertex)
        else:
            self.selectedVertices.append(self.hoverVertex)
        return True

    def selectAll(self):
        """(De)select all vertices"""
        if self.selectedVertices == self.graph.vertices and self.selectedVertices != []:
            self.selectedVertices = []
        elif self.graph.originalGraph:
            if self.selectedVertices == self.graph.originalGraph.vertices:
                self.selectedVertices = list(self.graph.vertices)
            else:
                self.selectedVertices = list(self.graph.originalGraph.vertices)
        else:
            self.selectedVertices = list(self.graph.vertices)
        self.redraw()

    def deselect(self):
        """Deselect all vertices"""
        self.selectedVertices = []
        self.redraw()

    def addVertex(self):
        """Add a vertex at the mouse position"""
        workGraph = self.graph.originalGraph if self.isTreeDecomposition else self.graph
        if self.hoverVertex != None or self.hoverEdge != None:
            return False
        if not workGraph.addVertex(Vertex(workGraph, len(workGraph.vertices), self.mainWin.mousePos)):
            return False
        self.hoverVertex = workGraph.vertices[-1]
        self.redraw()

    def addBag(self):
        """Add a bag at the mouse position"""
        if not self.isTreeDecomposition:
            return False
        if self.hoverVertex != None or self.hoverEdge != None:
            return False
        if not self.graph.addVertex(Bag(self.graph, len(self.graph.vertices), self.mainWin.mousePos)):
            return False
        self.hoverVertex = self.graph.vertices[-1]
        self.redraw()

    def removeVertices(self):
        """Remove the selected vertices"""
        self.redraw()
        pass

    def cliqueify(self):
        """Add or remove edges between all selected vertices"""
        if len(self.selectedVertices) < 2:
            return
        result = False
        workGraph = self.graph
        if self.isTreeDecomposition and type(self.selectedVertices[0]) != Bag:
            workGraph = self.graph.originalGraph
        # Add clique edges
        for a in self.selectedVertices:
            for b in self.selectedVertices:
                if a != b:
                    if workGraph.addEdge(a.vid, b.vid):
                        result = True
        # If no edges were added, remove all edges
        if not result:
            for a in self.selectedVertices:
                for b in self.selectedVertices:
                    if a.vid < b.vid:
                        workGraph.removeEdge(a.vid, b.vid)
        self.redraw()

    def pathify(self):
        """Creating a path, a tour or removing all edges between consecutive vertices"""
        if len(self.selectedVertices) < 2:
            return
        result = False
        workGraph = self.graph
        sv = self.selectedVertices
        if self.isTreeDecomposition and type(self.selectedVertices[0]) != Bag:
            workGraph = self.graph.originalGraph
        # Add path edges
        for i in range(len(sv) - 1):
            if workGraph.addEdge(sv[i].vid, sv[i + 1].vid):
                result = True
        # Add tour edge
        if not result:
            result = workGraph.addEdge(sv[0].vid, sv[-1].vid)
        # If no edges were added, remove all edges
        if not result:
            for i in range(len(sv) - 1):
                workGraph.removeEdge(sv[i].vid, sv[i + 1].vid)
            if len(sv) > 2:
                workGraph.removeEdge(sv[0].vid, sv[-1].vid)
        self.redraw()

    def treeify(self):
        """Connect or remove the first vertex to all others"""
        if len(self.selectedVertices) < 2:
            return
        result = False
        workGraph = self.graph
        sv = self.selectedVertices
        if self.isTreeDecomposition and type(self.selectedVertices[0]) != Bag:
            workGraph = self.graph.originalGraph
        # Add path edges
        r = sv[0]
        for v in sv[1:]:
            if workGraph.addEdge(r.vid, v.vid):
                result = True
        # If no edges were added, remove all edges
        if not result:
            for v in sv[1:]:
                workGraph.removeEdge(r.vid, v.vid)
        self.redraw()

    def toggleDrawText(self):
        """Toggle drawtext settings"""
        self.mainWin.settings.drawtext = not self.mainWin.settings.drawtext
        self.redraw()

    #
    # Dynamic Programming Algorithm
    #
    def tspDP(self): # Possible problem: how to make sure I get paths and not cycles.
        """Compute the smallest tour using DP on a tree decomposition"""
        if not self.isTreeDecomposition or len(self.graph.vertices) < 1:
            return
        Xroot = self.createRoot()
        S = self.fromDegrees([2] * len(Xroot.vertices))
        value = self.tspTable(S, Xroot)
        print("TSP cost: {}".format(value))
        # for nr, table in enumerate([self.graph.vertices[j].a for j in range(2)]):
        #     print('X{}'.format(nr))
        #     for i, v in enumerate(table):
        #         if v != None:
        #             print(' {}: {}'.format(self.toDegrees(i, 3), v))
        tour = self.tspReconstruct(S, Xroot)
        print('Tour: {}\n'.format(tour))

    def tspTable(self, S, Xi):
        # The smallest value such that all vertices below Xi have degree 2 and vertices in Xi have degrees defined by S
        debug = False
        if debug: print('=============================')
        if debug: print("A({}, X{}): {}".format(self.toDegrees(S, len(Xi.vertices)), Xi.vid, "?"))
        if Xi.a[S] != None:
            if debug: print('lookup return: {}'.format(Xi.a[S]))
            if debug: print('-----------------------------')
            return Xi.a[S]
        # We don't know this value yet, so we compute it.
        edges = []
        for v in Xi.vertices:
            for e in v.edges:
                if e.other(v) not in Xi.vertices:
                    continue
                if v.vid < e.other(v).vid:
                    edges.append(e)
        edges.sort(key=lambda e: e.cost)
        degrees = self.toDegrees(S, len(Xi.vertices))
        childDegrees = [[0] * len(degrees) for _ in Xi.edges]
        Xi.a[S] = self.tspRecurse(Xi, 0, 0, degrees, childDegrees, edges, [], self.tspChildEvaluation, min, sys.maxsize)
        if debug: print('calculation return: {}'.format(Xi.a[S]))
        if debug: print('-----------------------------')
        return Xi.a[S]

    def tspChildEvaluation(self, Xi, targetDegrees, childDegrees, validEdges, usedEdges, resultingEdgeList = None):
        # This method is the base case for the calculate tsp recurse method.
        # If we analyzed the degrees of all vertices (i.e. we have a complete combination),
        #   return the sum of B values of all children.
        debug = False
        # Base cost: the edges needed inside this Xi to account for the (target) degrees we didn't pass on to our children.
        val = self.tspEdgeSelect(sys.maxsize, 0, Xi, validEdges, targetDegrees, resultingEdgeList)
        if 0 <= val < sys.maxsize:
            if debug: print('{}Local edge selection cost: {}'.format('  ' * i, val))
            for k, cds in enumerate(childDegrees):
                Xkid = Xi.edges[k].other(Xi)
                if Xi.parent != Xkid:
                    # Strip off the vertices not in Xkid and add degrees 2 for vertices not in Xi
                    kidDegrees = [2] * len(Xkid.vertices)
                    for p, v in enumerate(Xkid.vertices):
                        for q, w in enumerate(Xi.vertices):
                            if v == w:
                                kidDegrees[p] = cds[q]
                    S = self.fromDegrees(kidDegrees)
                    if debug: print('{}temp A: {}, cds: {}, kidDegrees: {}'.format('  ' * i, S, cds, kidDegrees))
                    # Add to that base cost the cost of hamiltonian paths nescessary to satisfy the degrees.
                    val += self.tspTable(S, Xkid)
            if debug: print('{}Min cost for X{} with these child-degrees: {}'.format('  ' * i, Xi.vid, val))
        else:
            if debug: print('{}No local edge selection found'.format('  ' * i))
        return val

    def tspReconstruct(self, S, Xi):
        # Reconstruct the tsp tour (get a list of all edges)
        edges = []
        for v in Xi.vertices:
            for e in v.edges:
                if e.other(v) not in Xi.vertices:
                    continue
                if v.vid < e.other(v).vid:
                    edges.append(e)
        edges.sort(key=lambda e: e.cost)
        degrees = self.toDegrees(S, len(Xi.vertices))
        childDegrees = [[0] * len(degrees) for _ in Xi.edges]
        mergeF = lambda a, b: a + b
        return self.tspRecurse(Xi, 0, 0, degrees, childDegrees, edges, [], self.tspLookback, mergeF, [])

    def tspLookback(self, Xi, targetDegrees, childDegrees, validEdges, usedEdges):
        # This method is the base case for the reconstruct tsp recurse method.
        resultingEdgeList = [] # This list will be filled with the edges used in Xi
        totalDegrees = targetDegrees.copy()
        for cds in childDegrees:
            for i, d in enumerate(cds):
                totalDegrees[i] += d
        val = Xi.a[self.fromDegrees(totalDegrees)]
        if val == None:
            return []
        if val != self.tspChildEvaluation(Xi, targetDegrees, childDegrees, validEdges, usedEdges, resultingEdgeList):
            return []
        # So these are indeed the child degrees that we are looking for
        for k, cds in enumerate(childDegrees):
            Xkid = Xi.edges[k].other(Xi)
            if Xi.parent != Xkid:
                # Strip off the vertices not in Xkid and add degrees 2 for vertices not in Xi
                kidDegrees = [2] * len(Xkid.vertices)
                for p, v in enumerate(Xkid.vertices):
                    for q, w in enumerate(Xi.vertices):
                        if v == w:
                            kidDegrees[p] = cds[q]
                S = self.fromDegrees(kidDegrees)
                # We already got the resultingEdgeList for Xi, now add the REL for all the children
                resultingEdgeList += self.tspReconstruct(S, Xkid)
        return resultingEdgeList

    def tspRecurse(self, Xi, i, j, targetDegrees, childDegrees, validEdges, usedEdges, baseF, mergeF, defaultVal):
        # Select all possible mixes of degrees for all vertices and evaluate them
        #   i = the vertex we currently analyze, j = the child we currently analyze
        #   targetDegrees goes from full to empty, childDegrees from empty to full
        debug = False
        if debug: print('{}{}{}     (X{}: {}, {})   {}'.format('  ' * i, childDegrees, '  ' * (len(Xi.vertices) + 10 - i), Xi.vid, i, j, targetDegrees))
        # Final base case.
        if i >= len(Xi.vertices):
            return baseF(Xi, targetDegrees, childDegrees, validEdges, usedEdges)
        # Base case: if we can't or didn't want to 'spend' this degree, move on
        if targetDegrees[i] == 0 or j >= len(Xi.edges):
            return self.tspRecurse(Xi, i + 1, 0, targetDegrees, childDegrees, validEdges, usedEdges, baseF, mergeF, defaultVal)
        Xj = Xi.edges[j].other(Xi)
        # Base case: if the current bag (must be child) does not contain the vertex to analyze, try the next (child) bag
        if Xi.parent == Xi.edges[j].other(Xi) or Xi.vertices[i] not in Xj.vertices:
            return self.tspRecurse(Xi, i, j + 1, targetDegrees, childDegrees, validEdges, usedEdges, baseF, mergeF, defaultVal)

        # If the current degree is 2, try letting the child manage it
        result = defaultVal
        if targetDegrees[i] == 2 and childDegrees[j][i] == 0:
            td, cds = targetDegrees.copy(), [d.copy() for d in childDegrees]
            td[i] = 0
            cds[j][i] = 2
            result = self.tspRecurse(Xi, i + 1, 0, td, cds, validEdges, usedEdges, baseF, mergeF, defaultVal)
        # If the current degree is at least 1 (which it is if we get here),
        #   try to combine it (for all other vertices) in a hamiltonian path
        for k in range(i + 1, len(Xi.vertices)):
            # Todo: check if edge (i, k) is allowed (won't make it a cycle)
            if targetDegrees[k] < 1 or childDegrees[j][k] > 1 or Xi.vertices[k] not in Xj.vertices:
                continue
            td, cds = targetDegrees.copy(), [d.copy() for d in childDegrees]
            td[i] -= 1
            cds[j][i] += 1
            td[k] -= 1
            cds[j][k] += 1
            # We may have to try to analyze the same vertex again if it's degree is higher than 1
            result = mergeF(result, self.tspRecurse(Xi, i, j, td, cds, validEdges, usedEdges, baseF, mergeF, defaultVal))
        # Also, try not assigning this degree to anyone, we (maybe) can solve it inside Xi
        result = mergeF(result, self.tspRecurse(Xi, i, j + 1, targetDegrees, childDegrees, validEdges, usedEdges, baseF, mergeF, defaultVal))
        return result

    # Todo: use the minimum to abort early??? (is possible for leaf case, but perhaps not for normal bag case
    def tspEdgeSelect(self, minimum, index, Xi, edges, degrees, resultEdgeList = None):
        debug = False
        # Calculate the smallest cost to satisfy the degrees target using only using edges >= the index
        # Base case 1: the degrees are all zero, so we succeeded as we don't need to add any more edges
        satisfied = True
        for d in degrees:
            if d != 0:
                satisfied = False
                break
        if satisfied:
            if debug: print('Edge select ({}): no need to add edges, min value: 0'.format(index))
            return 0
        # Base case 2: we have not succeeded yet, but there are no more edges to add, so we failed
        if index >= len(edges):
            if debug: print('Edge select ({}): no more edges to add'.format(index))
            return sys.maxsize
        # Base case 3: one of the degrees is < 1, so we added too many vertices, so we failed [with side effect]
        edge = edges[index]
        deg = degrees.copy()
        assertCounter = 0
        for i, d in enumerate(deg):
            if Xi.vertices[i] == edge.a or Xi.vertices[i] == edge.b:
                if d < 0: # If it's negative it will tell us later
                          #  - can't return right now, as we need to evaluete not taking this edge as well.
                    if debug: print('Edge select ({}): too many edges added'.format(index))
                    return sys.maxsize
                # While checking this base case, also compute the new degree list for the first recursion
                deg[i] -= 1
                assertCounter += 1
        assert assertCounter in {0, 2}
        # Try both to take the edge and not to take the edge
        if debug: print('Edge select ({}), degrees: {}'.format(index, degrees))
        tempREL1, tempREL2 = [edge], []
        minimum = min(minimum, edge.cost + self.tspEdgeSelect(minimum - edge.cost, index + 1, Xi, edges, deg, tempREL1))
        val = self.tspEdgeSelect(minimum, index + 1, Xi, edges, degrees, tempREL2)
        if val < minimum:
            minimum = val
            # So without edge is better - Append the second edge list
            if resultEdgeList != None:
                for e in tempREL2:
                    resultEdgeList.append(e)
        # So without edge is not better - Append the first edge list
        elif resultEdgeList != None:
            for e in tempREL1:
                resultEdgeList.append(e)
        if debug: print('Edge select ({}): min value: {}, edges: {}'.format(index, minimum, resultEdgeList))
        return minimum

    def toDegrees(self, S, length=1):
        # From an integer representation to a list of degrees
        result = []
        while S != 0:
            temp = S
            S //= 3
            result.insert(0, temp - 3 * S)
        for _ in range(len(result), length):
            result.insert(0, 0)
        return result

    def fromDegrees(self, degrees):
        # From a list of degrees to an integer representation
        result = 0
        for d in degrees:
            result *= 3
            result += d
        return result

    def createRoot(self, rootBag=None):
        """Make the tree decomposition a true tree, by choosing a root and setting all parent pointers correctly"""
        # Choose the first bag as root if none is given
        if rootBag == None:
            rootBag = self.graph.vertices[0]
        # Define a local function that sets the parent of a bag recursively
        def setParentRecursive(bag, parent):
            bag.parent = parent
            bag.a, bag.b = [None] * (3 ** len(bag.vertices)), [None]
            if parent != None:
                bag.b = [None] * (3 ** len([None for v in bag.vertices if v in parent.vertices]))
            for e in bag.edges:
                child = e.other(bag)
                if not parent or bag.parent != child:
                    setParentRecursive(child, bag)
        # Set the parent for all bags
        setParentRecursive(rootBag, None)
        return rootBag

    #
    # Misc
    #
    def quit(self):
        """Quit"""
        self.mainWin.quit()

    def saveAs(self):
        """Save the graph to file"""
        origGraph = self.graph.originalGraph if self.isTreeDecomposition else self.graph
        s = "EDGE_WEIGHT_TYPE : EUC_2D"
        if origGraph.isEuclidean:
            s += ""
        s += "NODE_COORD_SECTION"
        for v in origGraph.vertices:
            s += "\n{} {} {}".format(v.vid, v.pos.x, v.pos.y)
        s += "\nEDGE_SECTION"
        for v in origGraph.vertices:
            for e in v.edges:
                if v.vid < e.other(v).vid:
                    s += "\n{} {} {}".format(e.a.vid, e.b.vid, e.cost)
        if self.isTreeDecomposition:
            s += "\nBAG_COORD_SECTION"
            for b in self.graph.vertices:
                s += "\n{} {} {}".format(b.vid, b.pos.x, b.pos.y)
                for v in b.vertices:
                    s += " " + str(v.vid)
            s += "\nBAG_EDGE_SECTION"
            for b in self.graph.vertices:
                for e in b.edges:
                    if e.a.vid < e.b.vid:
                        s += "\n{} {}".format(e.a.vid, e.b.vid)
        self.mainWin.app.broSave(s)

    def openFile(self):
        """Open a file"""
        path = self.mainWin.app.broOpen()
        # path = "test-graph-3.txt"
        # path = "graph-unittests.txt"
        self.openFileWithPath(path)

    def openFileWithPath(self, path):
        if path == "":
            return
        with open(path) as f:
            # Looks like the file opening went right. Good, now first create the new graph.
            self.graph = TreeDecomposition(Graph())
            origGraph = self.graph.originalGraph if self.isTreeDecomposition else self.graph
            comp = lambda line, s: line[0:len(s)] == s
            state = 0 # 0=nothing, 1=vertices, 2=edges, 3=bags, 4=bag edges

            # And lets now fill the graph with some sensible stuff.
            for line in f:
                l = line.split(' ')
                # Important file parameters
                if comp(line, "EDGE_WEIGHT_TYPE : EUC_2D"):
                     origGraph.isEuclidean = True
                # Vertices and edges
                elif comp(line, "NODE_COORD_SECTION"): state = 1
                elif comp(line, "EDGE_SECTION"): state = 2
                elif comp(line, "BAG_COORD_SECTION"): state = 3
                elif comp(line, "BAG_EDGE_SECTION"): state = 4
                # Add vertices, edges, bags or bag edges
                elif state == 1:
                    origGraph.addVertex(Vertex(origGraph, int(l[0]), Pos(int(l[1]), int(l[2]))))
                elif state == 2:
                    origGraph.addEdge(int(l[0]), int(l[1]), int(l[2]))
                elif state == 3:
                    bag = Bag(self.graph, int(l[0]), Pos(int(l[1]), int(l[2])))
                    for v in l[3:]:
                        bag.addVertex(origGraph.vertices[int(v)])
                    self.graph.addVertex(bag)
                elif state == 4:
                    self.graph.addEdge(int(l[0]), int(l[1]), 1)
        self.redraw()

    def keymapToStr(self):
        """Returns a string with all the keys and their explanation (docstring)."""
        result = ""
        for key, command in self.keymap.items():
            result += key + ": " + command.__doc__ + "\n"
        return result

