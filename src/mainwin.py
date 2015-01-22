from .win import *
from .colors import *
from .graph_interaction import *
import src.unittests


class MainWin(Win):
    def __init__(self, settings, app):
        Win.__init__(self, settings, app, Pos(0, 0))

        self.selectedScrollbar = -1 # Mark the scrollbar that is selected while a mousekey is down (1=vert, 2=hor)
        self.scrollImgs = None
        self.mousePos = Pos(-1, -1)
        self.mouseDownButton = -1
        self.mouseDownStartPos = Pos(-1, -1)
        self.redrawMarker = False

        self.graphInteraction = GraphInteraction(self)

        src.unittests.UnitTests(self)

    @property
    def isTreeDecomposition(self):
        return self.graphInteraction.isTreeDecomposition

    def redraw(self):
        """Mark the window for redrawing"""
        self.redrawMarker = True

    def draw(self):
        """Draw the main window"""
        # Draw myself
        self.fullClear()
        self.drawHelp()
        self.drawGraph(self.graphInteraction.graph)
        if self.isTreeDecomposition:
            self.drawGraph(self.graphInteraction.graph.originalGraph)

    def drawGraph(self, graph):
        """Draw the graph"""
        # The offset for selected vertices
        selectedVs = self.graphInteraction.selectedVertices
        offset = self.mousePos - self.mouseDownStartPos if self.mouseDownButton == 1 else Pos(0, 0)

        isTreeDecomposition = type(graph) == TreeDecomposition

        # Draw all edges
        for v in graph.vertices:
            for e in v.edges:
                if v.vid < e.other(v).vid:
                    ofsA = offset if v in selectedVs else Pos(0, 0)
                    ofsB = offset if e.other(v) in selectedVs else Pos(0, 0)
                    pa, pb = v.pos + ofsA, e.other(v).pos + ofsB
                    self.drawLine(self.colors.edge, pa, pb)
                    anchor = "nw" if (pa.x < pb.x) != (pa.y < pb.y) else "ne"
                    if not isTreeDecomposition:
                        self.drawString(str(e.cost), self.colors.hover, 0.5 * (pa + pb) + (0, 2), anchor)

        # Draw the hovered vertex
        isBag = type(self.graphInteraction.hoverVertex) == Bag
        if self.graphInteraction.hoverVertex and isTreeDecomposition == isBag:
            r = self.settings.selectradius + (self.settings.bagextra if isBag else 0)
            ofs = offset if self.graphInteraction.hoverVertex in selectedVs else Pos(0, 0)
            self.drawDisc(self.colors.hover, self.graphInteraction.hoverVertex.pos + ofs, r)

        # Draw all vertices
        for v in graph.vertices:
            # Draw the disc
            isBag = type(v) == Bag
            c = self.colors.normal if self.settings.drawsmall else self.colors.hover
            c = self.colors.selected if v in selectedVs else c
            r = self.settings.vertexradiussmall if self.settings.drawsmall else self.settings.vertexradiusbig
            if isBag: r += self.settings.bagextra
            ofs = offset if v in selectedVs else Pos(0, 0)
            self.drawDisc(c, v.pos + ofs, r)

            # Draw the text
            f = (lambda x: chr(x.vid + ord('a'))) if self.settings.drawtext else lambda x: str(x.vid)
            bagText = ""
            if isBag:
                bagText = "\n" if not v.parent else ("\nparent: " + f(v.parent) + "\n")
                bagText += "v: " + ' '.join(map(f, v.vertices))
            c = self.colors.selectedtext if v in selectedVs else self.colors.text
            self.drawString(f(v) + bagText, c, v.pos + ofs, 'c')

    def drawHelp(self):
        """Draw help text"""
        helptext = " Controls:\n-----------\n"
        helptext += self.graphInteraction.keymapToStr()
        self.drawString(helptext, self.colors.helptext, Pos(10, 10))

    def scrollbarClicks(self, p):
        # Manage scrollbar clicks
        vert, hor = self.settings.scrollbars in {'both', 'vertical'}, self.settings.scrollbars in {'both', 'horizontal'}
        barW = self.settings.scrollbarwidth
        # if vert:
        #     x, y = self.activeWin.pos.x + self.activeWin.size.w, self.activeWin.pos.y
        #     h = self.activeWin.size.h
        #     # Check if the user clicked somewhere in the (vertical) scrollbar region
        #     if x <= p.x <= x + barW and y <= p.y <= y + h:
        #         # The up button
        #         if p.y <= y + barW:
        #             self.activeWin.scrollText(True, -1)
        #         # The scrollbar (todo: split in two)
        #         elif p.y <= y + h - barW:
        #             posY = self.activeWin.calcScrollbarPos(True) + self.activeWin.pos.y
        #             if p.y < posY:
        #                 print('page up')
        #             elif p.y > posY + self.scrollImgs[2].height() + 2 * self.scrollImgs[2].width():
        #                 print('page down')
        #             else:
        #                 print('drag')
        #                 self.selectedScrollbar = 1
        #         # The down button
        #         else:
        #             self.activeWin.scrollText(True, 1)
        #         self.draw()
        # if hor:
        #     x, y = self.activeWin.pos.x, self.activeWin.pos.y + self.activeWin.size.h
        #     w = self.activeWin.size.w
        #     # Check if the user clicked somewhere in the (horizontal) scrollbar region
        #     if x <= p.x <= x + w and y <= p.y <= y + barW:
        #         # The left button
        #         if p.x <= x + barW:
        #             self.activeWin.scrollText(False, -1)
        #         # The scrollbar (todo: split in two)
        #         elif p.x <= x + w - barW:
        #             self.selectedScrollbar = 2
        #         # The right button
        #         else:
        #             self.activeWin.scrollText(False, 1)
        #         self.draw()

    def onMouseDown(self, p, btnNr):
        self.mouseDownStartPos = p
        if btnNr == 3:
            self.mouseDownButton = 3
            self.graphInteraction.keymap['RMB']()
        if btnNr == 1:
            self.mouseDownButton = 1
            self.graphInteraction.keymap['LMB']()
            # Hit scrollbar button
            self.scrollbarClicks(p)
    def onMouseDownDouble(self, p, btnNr):
        # Check scrollbar (you want to be able to click it multiple times close after eachother)
        if False:
            pass
        elif btnNr == 1:
            self.scrollbarClicks(p)
    def onMouseDownTriple(self, p, btnNr):
        # Forward triple click
        if False:
            pass
        # Check scrollbar (you want to be able to click it multiple times close after eachother)
        elif btnNr == 1:
            self.scrollbarClicks(p)

    def onMouseMove(self, p, btnNr):
        # Store the old hover vertex
        oldHoverVertex = self.graphInteraction.hoverVertex
        # Update the hovered vertex
        self.graphInteraction.hoverVertex = None
        distance = self.settings.selectradius
        for v in self.graphInteraction.graph.vertices:
            if p.distanceSqTo(v.pos) < distance * distance:
                distance = p.distanceTo(v.pos)
                self.graphInteraction.hoverVertex = v
        if self.graphInteraction.graph.originalGraph:
            distance = self.settings.selectradius + self.settings.bagextra
            for v in self.graphInteraction.graph.originalGraph.vertices:
                if p.distanceSqTo(v.pos) < distance * distance:
                    distance = p.distanceTo(v.pos)
                    self.graphInteraction.hoverVertex = v
        # (De)select vertices
        if self.mouseDownButton == 3 and oldHoverVertex != self.graphInteraction.hoverVertex:
            self.graphInteraction.keymap['RMB']()
        # Update the mouse position
        self.mousePos = p
        self.redraw()

    def onMouseScroll(self, p, factor):
        pass

    def onMouseUp(self, p, btnNr):
        # Deselect scrollbar
        self.selectedScrollbar = -1

        # Place vertices in a bag (or remove them)
        if self.isTreeDecomposition and type(self.graphInteraction.hoverVertex) == Bag:
            result = False
            for v in filter(lambda v: type(v) != Bag, self.graphInteraction.selectedVertices):
                if self.graphInteraction.hoverVertex.addVertex(v):
                    result = True
            if not result:
                for v in filter(lambda v: type(v) != Bag, self.graphInteraction.selectedVertices):
                    self.graphInteraction.hoverVertex.removeVertex(v)
        # Move vertices
        elif self.mouseDownButton == 1 and self.mouseDownStartPos != (-1, -1):
            for v in self.graphInteraction.selectedVertices:
                v.pos += p - self.mouseDownStartPos

        # Clean up
        self.mouseDownStartPos = Pos(-1, -1)
        self.mouseDownButton = -1

    def onKeyDown(self, c):
        if c in self.graphInteraction.keymap:
            self.graphInteraction.keymap[c]()

    def quit(self):
        """Quit the entire application"""
        self.app.master.quit()

    def resize(self, redraw=True):
        """Override the resize window"""
        self.size = self.settings.size

        self.initScrollImgs()

        if redraw:
            self.redraw()

    def loop(self):
        """This method is being called every n miliseconds (depending on the fps)"""
        # Draw if nescessary
        if self.redrawMarker:
            self.draw()
            self.redrawMarker = False

    #
    # Scroll images
    #
    def initScrollImgs(self):
        """Create the images for the scroll bars and buttons"""
        # Load all images and their pixel maps [bg, top, middle, bottom, bg, left, middle, right, up, right, down, left]
        pilImgs = [self.loadImgPIL(url) for url in ['scrollbg.png', 'scrolltop.png', 'scrollup.png']]
        self.settings.scrollbarwidth = pilImgs[0].size[0]
        w, h = pilImgs[1].size
        sq = Image.new('RGBA', (w, h))
        pilImgs[2:2] = [Image.new('RGBA', (w, 1)), sq, Image.new('RGBA', (1, self.settings.scrollbarwidth)), sq.copy(), Image.new('RGBA', (1, h)), sq.copy()]
        pilImgs.extend([sq.copy(), sq.copy(), sq.copy()])
        pixs = [t.load() for t in pilImgs]
        pixBgV, pixTop, pixMidV, pixBottom, pixBgH, pixLeft, pixMidH, pixRight, pixN, pixE, pixS, pixW = pixs

        # Paint the scroll images
        for img, pix in [(pilImgs[i], pixs[i]) for i in [1, 8]]:
            if img.mode in ['RGB', 'RGBA']:
                color = self.colors.toTuple(self.colors.scroll)
                diff = [color[i] - pix[w // 2, h // 2][i] for i in range(3)]
                temp = []
                for y in range(h):
                    for x in range(w):
                        temp = [min(255, max(0, pix[x, y][i] + diff[i])) for i in range(3)]
                        temp.append(pix[x, y][3])
                        pix[x, y] = tuple(temp)
        # Paint the background image
        if pilImgs[0].mode in ['RGB', 'RGBA']:
            color = self.colors.toTuple(self.colors.scrollbg)
            diff = [color[i] - pixBgV[0, 0][i] for i in range(3)]
            temp = []
            for x in range(self.settings.scrollbarwidth):
                temp = [min(255, max(0, pixBgV[x, 0][i] + diff[i])) for i in range(3)]
                if pilImgs[0].mode == 'RGBA':
                    temp.append(pixBgV[x, y][3])
                pixBgV[x, 0] = tuple(temp)

        # Create scroll bottom, right and left images
        for y in range(h):
            for x in range(w):
                pixBottom[x, y] = pixTop[x, h - 1 - y]
                pixLeft[x, y] = pixTop[y, x]
                pixRight[x, y] = pixTop[h - 1 - y, w - 1 - x]

        # Create the middle and bg images
        for i in range(self.settings.scrollbarwidth):
            pixBgH[0, i] = pixBgV[i, 0]
        for i in range(w):
            pixMidV[i, 0] = pixBottom[i, 0]
            pixMidH[0, i] = pixRight[0, i]
        otherBarExtra = self.settings.scrollbarwidth if self.settings.scrollbars == 'both' else 0
        pilImgs[0] = pilImgs[0].resize((self.settings.scrollbarwidth, self.settings.size.h - otherBarExtra), Image.NEAREST)
        pilImgs[2] = pilImgs[2].resize((w, 100), Image.NEAREST)
        pilImgs[4] = pilImgs[4].resize((self.settings.size.w - otherBarExtra, self.settings.scrollbarwidth), Image.NEAREST)
        pilImgs[6] = pilImgs[6].resize((100, h), Image.NEAREST)

        # Create the E, S, W images
        for y in range(h):
            for x in range(w):
                pixE[x, y] = pixN[h - 1 - y, w - 1 - x]
                pixS[x, y] = pixN[x, h - 1 - y]
                pixW[x, y] = pixN[y, x]

        # Convert the images to Tk images
        self.scrollImgs = [self.loadImgTk(img) for img in pilImgs]

