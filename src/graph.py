"""
This module contains my graph datastructures
"""
from .settings import *


#
# Graphs
#
class GraphBase():
    """An abstract graph base class"""
    def __init__(self, euclidean=False):
        self.vertices = []
        self.isEuclidean = euclidean
        self.name = ""
        pass

    def cost(self, vidA, vidB):
        raise NotImplementedError("Cost method is not implemented")

    def addVertex(self, vertex):
        """Add a vertex if it's not already in the list"""
        if vertex.vid != len(self.vertices):
            return False
        self.vertices.append(vertex)
        return True

    def addEdge(self, vidA, vidB, cost=0):
        raise NotImplementedError("Adding edges is not implemented")

    def removeEdge(self, vidA, vidB):
        raise NotImplementedError("Removing edges is not implemented")


class Graph(GraphBase):
    """A graph type where the vertices store their edges"""
    def __init__(self, euclidean=False):
        GraphBase.__init__(self, euclidean)

    def cost(self, vidA, vidB):
        edge = self.vertices[vidA].getEdgeTo(vidB)
        if edge != None:
            return edge.cost
        return sys.maxsize

    def addVertex(self, v):
        assert type(v) is Vertex, "Added vertices to this type of Graph must be of type 'Vertex'"
        return GraphBase.addVertex(self, v)

    def addEdge(self, vidA, vidB, cost=None):
        edge = Edge(self.vertices[vidA], self.vertices[vidB], cost)
        result = False
        if edge.a.addEdge(edge):
            result = True
        if edge.b.addEdge(edge):
            result = True
        return result

    def removeEdge(self, vidA, vidB):
        a, b = [self.vertices[vid] for vid in [vidA, vidB]]
        e = a.getEdgeTo(vidB)
        a.edges.remove(e)
        e = b.getEdgeTo(vidA)
        b.edges.remove(e)


class TreeDecomposition(Graph):
    """A tree decomposition of a graph"""
    def __init__(self, originalGraph):
        self.originalGraph = originalGraph
        GraphBase.__init__(self)

    def addVertex(self, v):
        if type(v) is Bag: # , "Added vertex must be of type 'Bag'"
            self.vertices.append(v)
            return True
        elif type(v) is Vertex:
            return self.originalGraph.addVertex(v)
        else:
            raise TypeError("Added vertex must be of type 'Vertex' or 'Bag'")


#
# Vertices
#
class VertexBase():
    """A vertex that doesn't store its edges"""
    def __init__(self, graph, vertexId, pos):
        self.graph = graph
        self.vid = vertexId
        self._pos = pos
        self.name = ""

    @property
    def pos(self):
        return self._pos
    @pos.setter
    def pos(self, value):
        self._pos = value


class Vertex(VertexBase):
    """A vertex that stores its edges itself"""
    def __init__(self, graph, vertexId, pos, edges=None):
        VertexBase.__init__(self, graph, vertexId, pos)
        self.edges = [] if edges == None else edges

    @VertexBase.pos.setter
    def pos(self, value):
        self._pos = value
        if self.graph.isEuclidean:
            for e in self.edges:
                e.euclideanCost()

    def addEdge(self, edge):
        """Add an edge if it's not already in the edge list"""
        if self != edge.a and self != edge.b:
            return False
        for e in self.edges:
            if e.isDuplicate(edge):
                return False
        self.edges.append(edge)
        assert edge.other(self) != None
        assert edge.other(edge.other(self)) != None
        return True

    def getEdgeTo(self, vid):
        # Returns the edge from this vertex to a vertex with vertex-id 'vid'
        for e in self.edges:
            if e.other(self):
                if e.other(self).vid == vid:
                    return e
        return None


class Bag(Vertex):
    def __init__(self, vertexId, pos, edges=None):
        Vertex.__init__(self, vertexId, pos, edges)
        self.vertices = [] # A list of pointers to the vertices in this bag.
        self.parent, self.a, self.b = None, None, None

    def addVertex(self, v):
        """Add a vertex from the original graph to this bag"""
        # assert v in self.originalGraph
        result = False
        if v not in self.vertices:
            self.vertices.append(v)
            result = True
        return result

    def removeVertex(self, v):
        """Remove a vertex from the bag"""
        if v in self.vertices:
            self.vertices.remove(v)
            return True
        return False


#
# Edges
#
class Edge():
    def __init__(self, a, b, cost=None):
        self.a = a
        self.b = b
        if cost == None:
            self.euclideanCost()
        else:
            self.cost = cost
        assert a != b

    def euclideanCost(self):
        x = self.a.pos.x - self.b.pos.x
        y = self.a.pos.y - self.b.pos.y
        self.cost = int(((x*x + y*y) ** 0.5) // 10) # The euclidean distance in deci-px.

    def other(self, vertex):
        if vertex == self.a:
            return self.b
        elif vertex == self.b:
            return self.a
        return None

    def isDuplicate(self, edge):
        return (edge.a == self.a and edge.b == self.b) or (edge.a == self.b and edge.b == self.a)

    def __repr__(self):
        return "({},{})".format(self.a.vid, self.b.vid)

