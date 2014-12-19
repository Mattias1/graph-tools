import sys
from .settings import *
from .graph import *
from contextlib import suppress


class GraphInteraction():
    def __init__(self, mainWin):
        self.initKeymap()
        self.graph = TreeDecomposition(Graph())
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
        if not workGraph.addVertex(Vertex(len(workGraph.vertices), self.mainWin.mousePos)):
            return False
        self.hoverVertex = workGraph.vertices[-1]
        self.redraw()

    def addBag(self):
        """Add a bag at the mouse position"""
        if not self.isTreeDecomposition:
            return False
        if self.hoverVertex != None or self.hoverEdge != None:
            return False
        if not self.graph.addVertex(Bag(len(self.graph.vertices), self.mainWin.mousePos)):
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
    # Algorithms
    #
    def tspDP(self): # Possible problem: how to make sure I get paths and not cycles.
        """Compute the smallest tour using DP on a tree decomposition"""
        if not self.isTreeDecomposition or len(self.graph.vertices) < 1:
            return
        root = self.createRoot()
        value = self.tspB(0, root)
        print(value)

    def tspA(self, S, Xi):
        print("A({}, X{}): {}".format(self.toDegrees(S), Xi.vid, "?"))
        # The smallest value such that all vertices below Xi have degree 2
        if Xi.a[S] != None:
            return Xi.a[S]
        edges = []
        for v in Xi.vertices:
            for e in v.edges:
                if v.vid < e.other(v).vid:
                    edges.append(e)
        edges.sort(key=lambda e: e.cost)
        # In the case of a leaf bag
        degrees = self.toDegrees(S)
        if len(Xi.edges) == 0 or (len(Xi.edges) == 1 and Xi.parent != None):
            Xi.a[S] = self.tspEdgeSelect(sys.maxsize, 0, edges, degrees.copy())
            return Xi.a[S]
        # In the case of a normal bag
        minimum = sys.maxsize
        # for s in range(3 ** len(Xi.vertices)):
        #     if S > s:
        #         continue # Todo: optimization + correctness???
        #     degrees = self.toDegrees(S - s)
        #     # Xi.a[S] = self.tspB(s, Xi) + self.tspEdgeSelect(sys.maxsize, 0, edges, degrees.copy())
        #     # TODO
        #     minimum = min(minimum, self.tspEdgeSelect(sys.maxsize, 0, edges, degrees.copy()))
        Xi.a[S] = minimum
        return Xi.a[S]

    def tspChildSelect(self, Xi, i, j, targetDegrees, childDegrees, usedEdges):
        # Select all possible mixes of degrees for all vertices and evaluate them
        #   i = the vertex we currently analyze, j = the child we currently analyze
        #   targetDegrees goes from full to empty, childDegrees from empty to full
        # Base case: if we analyzed the degrees of all vertices, return ???
        if i >= len(Xi.vertices):
            raise NotImplementedError("todo")
        # Base case: if we can't or didn't want to 'spend' this degree, move on
        if targetDegrees[i] == 0 or j >= len(Xi.edges):
            return self.tspChildSelect(Xi, i + 1, 0, targetDegrees, childDegrees, usedEdges)
        # Base case: if the current (child) bag does not contain the vertex to analyze, try the next (child) bag
        if Xi.vertices[i] not in Xi.edges[j].vertices:
            return self.tspChildSelect(Xi, i, j + 1, targetDegrees, childDegrees, usedEdges)

        # If the current degree is 2, try letting the child manage it
        if targetDegrees[i] == 2 and childDegrees[j][i] == 0:
            td, cds = targetDegrees.copy(), childDegrees.copy()
            td[i] = 0
            cds[j][i] = 2
            minimum = self.tspChildSelect(Xi, i + 1, 0, td, cds, usedEdges)
        # If the current degree is at least 1 (which it is if we get here),
        #   try to combine it (for all other vertices) in a hamiltonian path
        for k in range(i + 1, len(Xi.vertices)):
            # Todo: check if edge (i, k) is allowed (won't make it a cycle)
            if targetDegrees[k] < 1 or childDegrees[j] > 1:
                continue
            td, cds = targetDegrees.copy(), childDegrees.copy()
            td[i] -= 1
            cds[j][i] += 1
            td[k] -= 1
            cds[j][k] += 1
            # We may have to try to analyze the same vertex again if it's degree is higher than 1
            minimum = min(minimum, self.tspChildSelect(Xi, i, j, td, cds, usedEdges))
        # Also, try not assigning this degree to anyone, we (maybe) can solve it inside Xi
        minimum = min(minimum, self.tspChildSelect(Xi, i, j + 1, targetDegrees, childDegrees, usedEdges))
        return minimum

    # Todo: use the minimum to abort early??? (is possible for leaf case, but perhaps not for normal bag case
    def tspEdgeSelect(self, minimum, index, edges, degrees):
        # Calculate the smallest cost to satisfy the degrees target using only using edges >= the index
        # Base case 1: the degrees are all zero, so we succeeded as we don't need to add any more edges
        satisfied = True
        for d in degrees:
            if d != 0:
                satisfied = False
                break
        if satisfied:
            return 0
        # Base case 2: we have not succeeded yet, but there are no more edges to add, so we failed
        if index >= len(edges):
            return sys.maxsize
        # Base case 3: one of the degrees is < 1, so we added too many vertices, so we failed
        edge = edges[index]
        deg = degrees.copy()
        for i, d in enumerate(deg):
            if i == edge.a.vid or i == edge.b.vid:
                if d < 0:
                    return sys.maxsize
                # While checking this base case, also compute the new degree list for the first recursion
                deg[i] -= 1
        # Try both to take the edge and not to take the edge
        minimum = min(minimum, edge.cost + self.tspEdgeSelect(minimum - edge.cost, index + 1, edges, deg))
        minimum = min(minimum, self.tspEdgeSelect(minimum, index + 1, edges, degrees))
        return minimum

    def tspB(self, S, Xi):
        # The smallest value such that all vertices below Xi^Xp have degree 2
        if Xi.b[S] != None:
            return Xi.b[S]
        Xp = Xi.parent
        if Xp == None:
            Xp = Bag(-1, Pos(0, 0)) # In the case of the root vertex, cheat a little bit :)
        # Calculate the B value
        degrees = self.toDegrees(S)
        childDegrees = [None] * len(Xi.vertices)
        j = 0
        for i, v in enumerate(Xi.vertices):
            if v in Xp.vertices:
                try:
                    childDegrees[i] = degrees[j]
                    j += 1
                except IndexError:
                    childDegrees[i] = 0
            else:
                childDegrees[i] = 2
        Xi.b[S] = self.tspA(self.fromDegrees(childDegrees), Xi)
        return Xi.b[S]

    def toDegrees(self, S):
        # From an integer representation to a list of degrees
        result = []
        while S != 0:
            temp = S
            S //= 3
            result.append(temp - 3 * S)
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
        s = "NODE_COORD_SECTION"
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
                if comp(line, "NODE_COORD_SECTION"): state = 1
                elif comp(line, "EDGE_SECTION"): state = 2
                elif comp(line, "BAG_COORD_SECTION"): state = 3
                elif comp(line, "BAG_EDGE_SECTION"): state = 4
                # Add vertices, edges, bags or bag edges
                elif state == 1:
                    origGraph.addVertex(Vertex(int(l[0]), Pos(int(l[1]), int(l[2]))))
                elif state == 2:
                    origGraph.addEdge(int(l[0]), int(l[1]), int(l[2]))
                elif state == 3:
                    bag = Bag(int(l[0]), Pos(int(l[1]), int(l[2])))
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

