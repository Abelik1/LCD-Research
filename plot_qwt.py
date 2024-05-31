# -*- coding: utf-8 -*-

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
# from PyQt5.Qwt import *
from qwt import *
from plotpy import *
import globals

class Plot(QwtPlot):
    points = QPolygonF(4096)
    def __init__(self, parent=None):
        super(Plot, self).__init__(parent)
        self.setAxisTitle(QwtPlot.xBottom, 'Wavelength [nm]')
        self.setAxisTitle(QwtPlot.yLeft, 'Counts')
        self.setAxisScale(QwtPlot.xBottom, 200.0, 1600.0)
        self.setAxisScale(QwtPlot.yLeft, -500.0, 66000.0)
        self.curve = QwtPlotCurve("Curve 1")
        self.curve.setRenderHint(QwtPlotItem.RenderAntialiased)
        self.curve.setPen(QPen(Qt.black))
        self.curve.attach(self)
        self.zoomer = QwtPlotZoomer(self.canvas())
        self.zoomer.setMousePattern(QwtEventPattern.MouseSelect2, Qt.RightButton, Qt.ControlModifier)
        self.zoomer.setMousePattern(QwtEventPattern.MouseSelect3, Qt.RightButton)
        self.panner = QwtPlotPanner(self.canvas())
        self.panner.setMouseButton(Qt.MidButton)
        self.zoomer.setRubberBandPen(QColor(Qt.black))
        self.zoomer.setTrackerPen(QColor(Qt.black))
        self.replot()
        self.show()
        return

    def update_plot(self):
        self.points.clear()
        x = 0
        while (x < globals.pixels):   # 0 through 2047
           self.points.append(QPointF(float(globals.wavelength[x]), float(globals.spectraldata[x])))
           x += 1
        self.curve.setSamples(self.points)
        self.replot()
        self.show()    
        return


