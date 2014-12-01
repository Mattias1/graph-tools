from .settings import *
from .graph import *
from contextlib import suppress


class GraphInteraction():
    def __init__(self, mainWin):
        self.initKeymap()
        self.graph = Graph()
        self.hoverVertex = None
        self.hoverEdge = None
        self.selectedVertices = [] # List with vertex ids
        self.mainWin = mainWin

    def redraw(self):
        self.mainWin.redraw()

    def initKeymap(self):
        self.keymap = {
            'LMB': self.selectVertex,
            'RMB': self.selectVertex,
            'a': self.selectAll,
            'Esc': self.deselect,
            'v': self.addVertex,
            'd': self.removeVertices,
            'c': self.cliqueify,
            'Ctrl-c': self.quit
        }

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
        if len(self.selectedVertices) == len(self.graph.vertices):
            self.selectedVertices = []
        else:
            self.selectedVertices = list(self.graph.vertices)
        self.redraw()

    def deselect(self):
        """Deselect all vertices"""
        self.selectedVertices = []
        self.redraw()

    def addVertex(self):
        """Add a vertex at the mouse position"""
        if self.hoverVertex != None or self.hoverEdge != None:
            return False
        if not self.graph.addVertex(Vertex(len(self.graph.vertices), self.mainWin.mousePos)):
            return False
        self.hoverVertex = self.graph.vertices[-1]
        self.redraw()

    def removeVertices(self):
        """Remove the selected vertices"""
        self.redraw()
        pass

    def cliqueify(self):
        """Add or remove edges between all selected vertices"""
        result = False
        # Add clique edges
        for a in self.selectedVertices:
            for b in self.selectedVertices:
                if a != b:
                    if self.graph.addEdge(a.vid, b.vid):
                        result = True
        # If no edges were added, remove all edges
        if not result:
            for a in self.selectedVertices:
                for b in self.selectedVertices:
                    if a.vid < b.vid:
                        self.graph.removeEdge(a.vid, b.vid)
        self.redraw()

    def quit(self):
        """Quit"""
        self.mainWin.quit()

    def keymapToStr(self):
        """Returns a string with all the keys and their explanation (docstring)."""
        result = ""
        for key, command in self.keymap.items():
            result += key + ": " + command.__doc__ + "\n"
        return result

