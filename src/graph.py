"""
This module contains my graph datastructures
"""
from .settings import *


#
# Graphs
#
class GraphBase():
    """An abstract graph base class"""
    def __init__(self):
        self.vertices = []
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
    def __init__(self):
        GraphBase.__init__(self)

    def cost(self, vidA, vidB):
        edge = self.vertices[vidA].getEdgeTo(vidB)
        if edge:
            return edge.cost
        return inf

    def addVertex(self, v):
        assert type(v) is Vertex, "Added vertices to this type of Graph must be of type 'Vertex'"
        return GraphBase.addVertex(self, v)

    def addEdge(self, vidA, vidB, cost=0):
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


#
# Vertices
#
class VertexBase():
    """A vertex that doesn't store its edges"""
    def __init__(self, vertexId, pos):
        self.vid = vertexId
        self.pos = pos
        self.name = ""


class Vertex(VertexBase):
    """A vertex that stores its edges itself"""
    def __init__(self, vertexId, pos, edges=None):
        VertexBase.__init__(self, vertexId, pos)
        self.edges = [] if edges == None else edges

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


#
# Edges
#
class Edge():
    def __init__(self, a, b, cost):
        self.a = a
        self.b = b
        self.cost = cost
        assert a != b

    def other(self, vertex):
        if vertex == self.a:
            return self.b
        elif vertex == self.b:
            return self.a
        return None

    def isDuplicate(self, edge):
        return (edge.a == self.a and edge.b == self.b) or (edge.a == self.b and edge.b == self.a)

