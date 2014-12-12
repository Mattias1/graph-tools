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
            '1': self.toggleDrawText,
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
        if self.isTreeDecomposition:
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
            return False
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
            return False
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

    def toggleDrawText(self):
        """Toggle drawtext settings"""
        self.mainWin.settings.drawtext = not self.mainWin.settings.drawtext
        self.redraw()

    #
    # Algorithms
    #
    def tspDP(self):
        pass

    #
    # Misc
    #
    def quit(self):
        """Quit"""
        self.mainWin.quit()

    def keymapToStr(self):
        """Returns a string with all the keys and their explanation (docstring)."""
        result = ""
        for key, command in self.keymap.items():
            result += key + ": " + command.__doc__ + "\n"
        return result

