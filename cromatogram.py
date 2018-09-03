__author__ = 'Toni'

import numpy as np
import numpy.random as rnd
from PyQt4.QtCore import QString, QTimer, Qt
from PyQt4.QtGui import *
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from matplotlibwidget import MatplotlibWidget
from cromatogram_w import Ui_CromWindow
from trasmission import color2str, generate_colors

try:
    _fromUtf8 = QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QApplication.UnicodeUTF8


    def _translate(context, text, disambig):
        return QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QApplication.translate(context, text, disambig)


class Cromatogram(QMainWindow):
    def __init__(self, parent, tmodel):
        QMainWindow.__init__(self, parent)
        self.ui = Ui_CromWindow()
        self.ui.setupUi(self)
        self.tmodel = tmodel

        # Creates the matplotlib window and the toolbar
        self.mpl_window = MatplotlibWidget()
        self.ui.vl_plot.addWidget(self.mpl_window)
        self.toolbar = NavigationToolbar(self.mpl_window, self)
        self.ui.vl_plot.addWidget(self.toolbar)
        self.color_list = generate_colors(self.tmodel.num_analites)
        # Plot the models
        conc = self.simulate()
        self.plot(conc)

    def simulate(self):
        """ This function simulate the exit of each analito through the column. """
        full_concentration = 0.998

        tmodel = self.tmodel

        if not tmodel.is_ideal_type:
            full_concentration = 0.5

        last_plate_conc = np.zeros(tmodel.num_analites)

        concentration = []
        for i in np.arange(tmodel.num_analites):
            concentration.append([])

        k = 0
        while True:
            tmodel.max_iter += 1
            tmodel.update(1)

            for i in np.arange(tmodel.num_analites):
                # amount of concentration in last plate
                aux = tmodel.current_state[4][i][tmodel.num_teo_plates - 1]
                last_plate_conc[i] += aux
                concentration[i].append(aux)

            flag = True
            for i in np.arange(tmodel.num_analites):
                if last_plate_conc[i] < full_concentration * tmodel.conc_initial[i]:
                    flag = False

            if flag:
                # print last_plate_conc
                # print tmodel.conc_initial
                break

            k += 1

        return k + 1, concentration

    def plot(self, concentrations):

        for i in np.arange(self.tmodel.num_analites):
            self.mpl_window.axes.set_xlabel("Numero de Iteraciones")
            self.mpl_window.axes.set_ylabel("Concentracion")
            # print concentrations[0], len(concentrations[i + 1])
            self.mpl_window.axes.plot(np.arange(concentrations[0]), concentrations[1][i], color2str(self.color_list[i]),
                                      label=str(chr(65 + i)))
            self.mpl_window.axes.hold(True)

        self.mpl_window.axes.grid()
        self.mpl_window.axes.legend()
        self.mpl_window.draw()
