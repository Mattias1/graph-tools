# import cProfile
import sys
import json
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

        # LOL, this is actually nescessary for some graphs (500 vertices)
        sys.setrecursionlimit(2000)

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
            '2': self.toggleDrawSize,
            '-': self.zoomOut,
            '+': self.zoomIn,
            '=': self.resetZoom,
            'q': self.tspDP,
            'w': self.tikz,
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
        for v in self.selectedVertices:
            if type(v) == Bag:
                self.graph.removeVertex(v)
            else:
                self.graph.originalGraph.removeVertex(v)
        self.selectedVertices = []
        self.redraw()

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
        """Create a path, a tour or remove all edges between consecutive vertices"""
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
    def toggleDrawSize(self):
        """Toggle draw size settings"""
        self.mainWin.settings.drawsize = (self.mainWin.settings.drawsize + 1) % 3
        self.redraw()

    def zoomOut(self):
        """Zoom out"""
        self.mainWin.scaleFactor /= 2
        self.redraw()
    def zoomIn(self):
        """Zoom in"""
        self.mainWin.scaleFactor *= 2
        self.redraw()
    def resetZoom(self):
        """Reset zoom"""
        self.mainWin.scaleFactor = 1
        self.redraw()

    #
    # Parse to tikz
    #
    def tikz(self):
        """Output the LaTeX tikz-code that draws the current graph (and TD)"""
        # Some configuration that might (or might not) be usefull to have in the LaTeX document.
        #   \tikzstyle{vertex2} = [circle,fill=black!25,minimum size=18pt,align=center,font=\tiny]
        #   \tikzstyle{vertex1} = [circle,fill=black!25,minimum size=8pt,align=center,font=\tiny]
        #   \tikzstyle{vertex0} = [circle,minimum size=1pt]
        #   \tikzstyle{bag} = [circle,fill=black!25,minimum size=35pt,align=center,text width=35pt,font=\tiny]
        #   \tikzstyle{edge} = [draw,-]
        #   \tikzstyle{arc} = [draw,->-]
        #   \tikzstyle{weight} = [font=\small]
        z = 1 / 100
        print(r"\begin{figure}")
        print(r"\centering")
        print(r"\begin{tikzpicture}[auto,swap]")

        for v in self.graph.originalGraph.vertices:
            print(r"\node[vertex{}] ({}) at ({:.2}, {:.2}) {{{}}};".format(
                self.mainWin.settings.drawsize, v.vid, v.pos.x * z, -v.pos.y * z, v.vid
            ))

        for v in self.graph.originalGraph.vertices:
            for e in v.edges:
                print(r"\path[edge] ({}) to ({});".format(v.vid, e.other(v).vid))

        for b in self.graph.vertices:
            print(r"\node[bag] ({}) at ({:.2}, {:.2}) {{{}: {}}};".format(
                b.vid, b.pos.x * z, -b.pos.y * z, b.vid, str([v.vid for v in b.vertices])[1:-1]
            ))

        for b in self.graph.vertices:
            for e in b.edges:
                print(r"\path[edge] ({}) to ({});".format(b.vid, e.other(b).vid))

        print(r"\end{tikzpicture}")
        print(r"\caption{TODO}")
        print(r"\end{figure}")

    #
    # Dynamic Programming Algorithm
    #
    def tspDP(self):
        """Temp tsp"""
        # cProfile.runctx('self.temptemptemp()', globals(), locals())
        self.temptemptemp()

    def temptemptemp(self):
        """Compute the smallest tour using DP on a tree decomposition"""
        if not self.isTreeDecomposition or len(self.graph.vertices) < 1:
            return
        Xroot = self.createRoot()
        S = self.fromDegreesEndpoints([2] * len(Xroot.vertices), [])
        value = self.tspTable(S, Xroot)
        print("TSP cost: {}".format(value))
        for nr, table in enumerate([bag.a for bag in self.graph.vertices]):
            print('X{}'.format(nr))
            for key, val in table.items():
                print('  {}: {}'.format(key, val))
        if value < sys.maxsize:
            tour = list(set(self.tspReconstruct(S, Xroot)))
            print('\nDP-TSP:\n  Length: {}\n  Tour: {}\n'.format(value, tour))

    def tspTable(self, S, Xi):
        # The smallest value such that all vertices below Xi have degree 2 and vertices in Xi have degrees defined by S
        debug = False
        if debug: print("A({} {}, X{}): {}".format(self.toDegrees(S), self.toEndpoints(S), Xi.vid, "?"))
        if S in Xi.a:
            if debug: print('lookup return: {}'.format(Xi.a[S]))
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
        degrees = self.toDegrees(S)
        endpoints = self.toEndpoints(S)
        childEndpoints = [[] for _ in Xi.edges]
        childDegrees = [[0] * len(degrees) for _ in Xi.edges]
        Xi.a[S] = self.tspRecurse(Xi, edges, 0, 0, degrees, childDegrees, endpoints, childEndpoints,
                                    self.tspChildEvaluation, min, sys.maxsize)
        if debug: print('calculation return: {}'.format(Xi.a[S]))
        return Xi.a[S]

    def tspChildEvaluation(self, Xi, edges, targetDegrees, childDegrees, endpoints, childEndpoints, resultingEdgeList = None):
        # This method is the base case for the calculate tsp recurse method.
        # If we analyzed the degrees of all vertices (i.e. we have a complete combination),
        #   return the sum of B values of all children.
        debug = False
        # Check: all bags (except the root) are not allowed to be a cycle.
        if not endpoints and Xi.parent:
            if debug: print('{}All bags should be a cycle - no endpoints given'.format('  ' * len(Xi.vertices)))
            return sys.maxsize
        # Base cost: the edges needed inside this Xi to account for the (target) degrees we didn't pass on to our children.
        allChildEndpoints = sum(childEndpoints, []) # Flatten the list
        val = self.tspEdgeSelect(sys.maxsize, 0, Xi, edges, targetDegrees, endpoints, allChildEndpoints, resultingEdgeList)
        if 0 <= val < sys.maxsize:
            if debug: print('{}Local edge selection cost: {}, edges: {}, degrees: {}, endpoints: {}, edgeList: {}'.format(
                                            '  ' * len(Xi.vertices), val, edges, targetDegrees, endpoints, resultingEdgeList))
            for k, cds in enumerate(childDegrees):
                Xkid = Xi.edges[k].other(Xi)
                if Xi.parent != Xkid:
                    # Strip off the vertices not in Xkid and add degrees 2 for vertices not in Xi
                    kidDegrees = [2] * len(Xkid.vertices)
                    for p, v in enumerate(Xkid.vertices):
                        for q, w in enumerate(Xi.vertices):
                            if v == w:
                                kidDegrees[p] = cds[q]
                    S = self.fromDegreesEndpoints(kidDegrees, childEndpoints[k])
                    if debug: print('{}child A: {}, cds: {}, degrees: {}, endpoints: {}'.format('  ' * len(Xi.vertices),
                                                                    val, cds, kidDegrees, childEndpoints[k]))
                    # Add to that base cost the cost of hamiltonian paths nescessary to satisfy the degrees.
                    val += self.tspTable(S, Xkid)
            if debug: print('{}Min cost for X{} with these child-degrees: {}'.format('  ' * len(Xi.vertices), Xi.vid, val))
        else:
            if debug: print('{}No local edge selection found'.format('  ' * len(Xi.vertices)))
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
        degrees = self.toDegrees(S)
        endpoints = self.toEndpoints(S)
        childEndpoints = [[] for _ in Xi.edges]
        childDegrees = [[0] * len(degrees) for _ in Xi.edges]
        mergeF = lambda a, b: a + b
        return self.tspRecurse(Xi, edges, 0, 0, degrees, childDegrees, endpoints, childEndpoints, self.tspLookback, mergeF, [])

    def tspLookback(self, Xi, edges, targetDegrees, childDegrees, endpoints, childEndpoints):
        # This method is the base case for the reconstruct tsp recurse method.
        debug = False
        resultingEdgeList = [] # This list will be filled with the edges used in Xi
        totalDegrees = targetDegrees.copy()
        for cds in childDegrees:
            for i, d in enumerate(cds):
                totalDegrees[i] += d
        val = Xi.a[self.fromDegreesEndpoints(totalDegrees, endpoints)]
        if val == None:
            return []
        if val != self.tspChildEvaluation(Xi, edges, targetDegrees, childDegrees, endpoints, childEndpoints, resultingEdgeList):
            return [] # Side effect above intended to fill the edge list
        if debug: print('X{} edgelist 1: {}'.format(Xi.vid, resultingEdgeList))
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
                S = self.fromDegreesEndpoints(kidDegrees, childEndpoints[k])
                # We already got the resultingEdgeList for Xi, now add the REL for all the children
                resultingEdgeList += self.tspReconstruct(S, Xkid)
                # print('test 2 edgelist: {}'.format(resultingEdgeList))
        if debug: print('X{} edgelist 3: {}'.format(Xi.vid, resultingEdgeList))
        return resultingEdgeList

    def tspRecurse(self, Xi, edges, i, j, targetDegrees, childDegrees, endpoints, childEndpoints, baseF, mergeF, defaultVal):
        # Select all possible mixes of degrees for all vertices and evaluate them
        #   i = the vertex we currently analyze, j = the child we currently analyze
        #   targetDegrees goes from full to empty, childDegrees from empty to full, endpoints are the endpoints for each child path
        debug = False and isinstance(defaultVal, int)
        if debug: print('{}{}{}     (X{}: {}, {})   {}|{}'.format('  ' * i, childDegrees, '  ' * (len(Xi.vertices) + 8 - i), Xi.vid, i, j, targetDegrees, endpoints))
        # Final base case.
        if i >= len(Xi.vertices):
            return baseF(Xi, edges, targetDegrees, childDegrees, endpoints, childEndpoints)
        # Base case: if we can't or didn't want to 'spend' this degree, move on
        if targetDegrees[i] == 0 or j >= len(Xi.edges):
            return self.tspRecurse(Xi, edges, i + 1, 0, targetDegrees, childDegrees, endpoints, childEndpoints,
                                    baseF, mergeF, defaultVal)
        Xj = Xi.edges[j].other(Xi)
        # Base case: if the current bag (must be child) does not contain the vertex to analyze, try the next (child) bag
        if Xi.parent == Xi.edges[j].other(Xi) or Xi.vertices[i] not in Xj.vertices:
            return self.tspRecurse(Xi, edges, i, j + 1, targetDegrees, childDegrees, endpoints, childEndpoints,
                                    baseF, mergeF, defaultVal)

        # If the current degree is 2, try letting the child manage it
        result = defaultVal
        if targetDegrees[i] == 2 and childDegrees[j][i] == 0:
            td, cds = targetDegrees.copy(), [d.copy() for d in childDegrees]
            td[i] = 0
            cds[j][i] = 2
            result = self.tspRecurse(Xi, edges, i + 1, 0, td, cds, endpoints, childEndpoints, baseF, mergeF, defaultVal)
        # If the current degree is at least 1 (which it is if we get here),
        #   try to combine it (for all other vertices) in a hamiltonian path
        for k in range(i + 1, len(Xi.vertices)):
            # Stay in {0, 1, 2}
            if targetDegrees[k] < 1 or childDegrees[j][k] > 1 or Xi.vertices[k] not in Xj.vertices:
                continue
            # Don't add edges twice
            if self.inEndpoints(childEndpoints[j], Xi.vertices[i].vid, Xi.vertices[k].vid):
                continue
            td, cds, eps = targetDegrees.copy(), [d.copy() for d in childDegrees], [ep.copy() for ep in childEndpoints]
            td[i] -= 1
            cds[j][i] += 1
            td[k] -= 1
            cds[j][k] += 1
            eps[j].extend([Xi.vertices[nr].vid for nr in [i, k]])


            # DEBUG DEBUG DEBUG
            for test1 in range(len(eps[j]) - 1):
                for test2 in range(test1 + 1, len(eps[j])):
                    if eps[j][test1] == eps[j][test2]:
                        print("NOOOOOOOOOOOOOOOO! - some endpoints are occuring twice in the eps list: {}".format(eps[j]));


            # We may have to try to analyze the same vertex again if it's degree is higher than 1
            result = mergeF(result, self.tspRecurse(Xi, edges, i, j, td, cds, endpoints, eps, baseF, mergeF, defaultVal))
        # Also, try not assigning this degree to anyone, we (maybe) can solve it inside Xi
        result = mergeF(result, self.tspRecurse(Xi, edges, i, j + 1, targetDegrees, childDegrees,
                                                        endpoints, childEndpoints, baseF, mergeF, defaultVal))
        return result

    # Todo: use the minimum to abort early??? (is possible for leaf case, but perhaps not for normal bag case
    def tspEdgeSelect(self, minimum, index, Xi, edges, degrees, endpoints, allChildEndpoints, edgeList = None):
        # Calculate the smallest cost to satisfy the degrees target using only using edges >= the index
        debug = False
        # Base case 1: the degrees are all zero, so we succeeded as we don't need to add any more edges
        satisfied = True
        for d in degrees:
            if d != 0:
                satisfied = False
                break
        if satisfied:
            # So we have chosen all our edges and satisfied the targets - now make sure there is no cycle (unless root)
            if not self.cycleCheck(endpoints, edgeList, allChildEndpoints):
                if debug: print('Edge select ({}): edges contain a cycle'.format(index))
                return sys.maxsize
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
        tempEL = [] if edgeList == None else edgeList.copy()
        tempEL1, tempEL2 = tempEL + [edge], tempEL.copy()
        minimum = min(minimum, edge.cost + self.tspEdgeSelect(minimum - edge.cost, index + 1, Xi, edges,
                                                                    deg, endpoints, allChildEndpoints, tempEL1))
        val = self.tspEdgeSelect(minimum, index + 1, Xi, edges, degrees, endpoints, allChildEndpoints, tempEL2)
        if val < minimum:
            minimum = val
            # So without edge is better - Append the second edge list
            if edgeList != None:
                for e in tempEL2:
                    edgeList.append(e)
        # So without edge is not better - Append the first edge list
        elif edgeList != None:
            for e in tempEL1:
                edgeList.append(e)
        if debug: print('Edge select ({}): min value: {}, edges: {}'.format(index, minimum, edgeList))
        return minimum

    def toDegrees(self, S):
        # From a string representation to a list of degrees
        return json.loads(S.split('|')[0])

    def toEndpoints(self, S):
        # From a string representation to a list of edges
        return json.loads(S.split('|')[1])

    def fromDegreesEndpoints(self, degrees, endpoints):
        # From a list of degrees and endpoints to a string representation
        return json.dumps(degrees) + '|' + json.dumps(endpoints)

    def createRoot(self, rootBag=None):
        """Make the tree decomposition a true tree, by choosing a root and setting all parent pointers correctly"""
        # Choose the first bag as root if none is given
        if rootBag == None:
            rootBag = self.graph.vertices[0]
        # Define a local function that sets the parent of a bag recursively
        def setParentRecursive(bag, parent):
            bag.parent = parent
            bag.a = {}
            for e in bag.edges:
                child = e.other(bag)
                if not parent or bag.parent != child:
                    setParentRecursive(child, bag)
        # Set the parent for all bags
        setParentRecursive(rootBag, None)
        return rootBag

    def cycleCheck(self, endpoints, edgeList, allChildEndpoints):
        # This method returns whether or not the given edge list and all child endpoints provide a set of paths
        # satisfying the endpoints and sorts the edge list in place.
        debug = False
        progressCounter, edgeCounter, endpsCounter, v = -2, 0, 0, None
        if edgeList == None: edgeList = []

        # Special case: the root bag.
        if endpoints == []:
            if len(allChildEndpoints) > 0:
                endpoints = allChildEndpoints[:2]
                endpsCounter += 2
            elif len(edgeList) > 0:
                endpoints = [edgeList[0].a.vid, edgeList[0].b.vid]
                edgeCounter += 1
            else:
                if debug: print('ERROR: cycle check root bag has both no edges to add, nor any child endpoints')
                return False

        # Normal case
        while True:
            # Dump the state
            if debug:
                print('cycle check dump 1:')
                print('  endpoints: {}'.format(endpoints))
                print('  edgeList: {} - {}'.format(edgeCounter, edgeList))
                print('  kid endpoints: {} - {}'.format(endpsCounter, allChildEndpoints))
                print('  progress: {} - v: {}\n'.format(progressCounter, -1 if not v else v.vid))

            # If we completed the path
            if v == None or v.vid == endpoints[progressCounter + 1]:
                progressCounter += 2
                if progressCounter >= len(endpoints):
                    if edgeCounter == len(edgeList) and endpsCounter == len(allChildEndpoints):
                        return True
                    else:
                        if debug: print('ERROR: all endpoints are satisfied, but there are edges or endpoints left')
                        return False
                v = self.graph.originalGraph.vertices[endpoints[progressCounter]]

            # Dump the state
            if debug:
                print('cycle check dump 2:')
                print('  endpoints: {}'.format(endpoints))
                print('  edgeList: {} - {}'.format(edgeCounter, edgeList))
                print('  kid endpoints: {} - {}'.format(endpsCounter, allChildEndpoints))
                print('  progress: {} - v: {}\n'.format(progressCounter, -1 if not v else v.vid))

            # Find the next vertex
            for i in range(endpsCounter, len(allChildEndpoints), 2):
                if v.vid in allChildEndpoints[i : i + 2]:
                    v = self.graph.originalGraph.vertices[allChildEndpoints[i + 1 if v.vid == allChildEndpoints[i] else i]]
                    allChildEndpoints[endpsCounter : endpsCounter + 2], allChildEndpoints[i : i + 2] = allChildEndpoints[
                                                            i : i + 2], allChildEndpoints[endpsCounter : endpsCounter + 2]
                    endpsCounter += 2
                    break
            else:
                for i in range(edgeCounter, len(edgeList)):
                    if v in edgeList[i]:
                        v = edgeList[i].other(v)
                        edgeList[edgeCounter], edgeList[i] = edgeList[i], edgeList[edgeCounter]
                        edgeCounter += 1
                        break
                else:
                    if debug: print('eps: {}, edgelist: {}, all kid eps: {}'.format(endpoints, edgeList, allChildEndpoints))
                    if debug: print('ERROR, no more endpoints or edges found according to specs')
                    return False
        if debug: print('ERROR: The code should not come here')
        return False

    def inEndpoints(self, endpoints, start, end):
        # Return whether or not this combination of endpoints (or reversed order) is already in the endpoints list
        for j in range(0, len(endpoints), 2):
            if (endpoints[j] == start and endpoints[j + 1] == end) or (endpoints[j + 1] == start and endpoints[j] == end):
                return True
        return False

    #
    # Misc
    #
    def quit(self):
        """Quit"""
        self.mainWin.quit()

    def saveAs(self):
        """Save the graph to file"""
        origGraph = self.graph.originalGraph if self.isTreeDecomposition else self.graph
        vidStart = self.mainWin.settings.vidStart
        s = ""
        s += "DIMENSION : {}\n".format(len(origGraph.vertices))
        if origGraph.isEuclidean:
            s += "EDGE_WEIGHT_TYPE : EUC_2D\n"
        s += "NODE_COORD_SECTION\n"
        for v in origGraph.vertices:
            s += "{} {} {}\n".format(v.vid + vidStart, v.pos.x, v.pos.y)
        s += "EDGE_SECTION\n"
        for v in origGraph.vertices:
            for e in v.edges:
                if v.vid < e.other(v).vid:
                    s += "{} {} {}\n".format(e.a.vid + vidStart, e.b.vid + vidStart, e.cost)
        if self.isTreeDecomposition:
            s += "BAG_COORD_SECTION\n"
            for b in self.graph.vertices:
                s += "{} {} {}".format(b.vid + vidStart, b.pos.x, b.pos.y)
                for v in b.vertices:
                    s += " " + str(v.vid)
                s += "\n"
            s += "BAG_EDGE_SECTION\n"
            for b in self.graph.vertices:
                for e in b.edges:
                    if e.a.vid < e.b.vid:
                        s += "{} {}\n".format(e.a.vid + vidStart, e.b.vid + vidStart)
        self.mainWin.app.broSave(s, True)

    def openFile(self):
        """Open a file"""
        path = self.mainWin.app.broOpen()
        self.openFileWithPath(path)

    def openFileWithPath(self, path):
        if path == "":
            return
        with open(path) as f:
            # Looks like the file opening went right. Good, now first create the new graph.
            self.graph = TreeDecomposition(Graph(False))
            origGraph = self.graph.originalGraph if self.isTreeDecomposition else self.graph
            self.mainWin.app.setTitle()
            comp = lambda line, s: line[0:len(s)] == s
            state = 0 # 0=nothing, 1=vertices, 2=edges, 3=bags, 4=bag edges
            vidStart = self.mainWin.settings.vidStart

            # And lets now fill the graph with some sensible stuff.
            for line in f:
                l = line.strip().split(' ')
                # Important file parameters
                if comp(line, "NAME : "):
                    self.graph.name = l[2]
                    origGraph.name = l[2]
                    self.mainWin.app.setTitle(l[2])
                elif comp(line, "EDGE_WEIGHT_TYPE : EUC_2D"):
                     origGraph.isEuclidean = True
                # Vertices and edges
                elif comp(line, "NODE_COORD_SECTION"): state = 1
                elif comp(line, "EDGE_SECTION"): state = 2
                elif comp(line, "BAG_COORD_SECTION"): state = 3
                elif comp(line, "BAG_EDGE_SECTION"): state = 4
                elif comp(line, "DEMAND_SECTION"): state = 5
                elif comp(line, "DEPOT_SECTION"): state = 6
                # Add vertices, edges, bags or bag edges
                elif state == 1:
                    origGraph.addVertex(Vertex(origGraph, int(l[0]) - vidStart, Pos(int(l[1]), int(l[2]))))
                elif state == 2:
                    origGraph.addEdge(int(l[0]) - vidStart, int(l[1]) - vidStart, int(l[2]))
                elif state == 3:
                    bag = Bag(self.graph, int(l[0]) - vidStart, Pos(int(l[1]), int(l[2])))
                    for v in l[3:]:
                        bag.addVertex(origGraph.vertices[int(v) - vidStart])
                    self.graph.addVertex(bag)
                elif state == 4:
                    self.graph.addEdge(int(l[0]) - vidStart, int(l[1]) - vidStart, 1)

        # Change some settings for large graphs
        if len(origGraph.vertices) > 30:
            self.mainWin.settings.drawtext = False
            self.mainWin.settings.drawsize = 0
            for _ in range(5):
                self.zoomOut()
        self.redraw()

    def keymapToStr(self):
        """Returns a string with all the keys and their explanation (docstring)."""
        result = ""
        for key, command in sorted(self.keymap.items()):
            result += key + ": " + command.__doc__ + "\n"
        return result

