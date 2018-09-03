__author__ = 'Toni'

import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from main_w import Ui_MainWindow
from trasmission import Trasmission
from cromatogram import Cromatogram
from model import Model
import numpy as np
import numpy.random as rnd

# Some experiments constants
DEFAULT_CONCENTRATION = 10

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


class Main(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Load the process image of the main window
        proc_img = QPixmap("./images/process_img.png").scaledToWidth(300)
        self.ui.lb_proc_img.setPixmap(proc_img)
        self.adjustTable()

        # Connect the events to keep the configuration settings
        # updated

        self.ui.sb_num_analites.valueChanged.connect(self.adjustTable)
        self.ui.pb_trasmission.clicked.connect(self.go_to_transmission)
        self.ui.pb_crom.clicked.connect(self.go_to_cromatogram)
        # self.ui.tbw_analites_info.itemPressed.connect(self.initKs)

    def adjustTable(self):
        n = self.ui.sb_num_analites.value()
        self.ui.tbw_analites_info.setRowCount(n)
        for i in np.arange(n):
            self.ui.tbw_analites_info.setItem(i, 0, QTableWidgetItem(str(chr(65 + i))))
            self.ui.tbw_analites_info.setItem(i, 1, QTableWidgetItem(str(round(rnd.rand(), 3) * DEFAULT_CONCENTRATION)))
            self.ui.tbw_analites_info.setItem(i, 2, QTableWidgetItem(str(75 + round(rnd.rand(), 3) * 50)))

    def collect_model(self):
        # Collect the configuration of the model to simulate
        ideal = self.ui.rb_eluc_isoc.isChecked()
        num_analites = self.ui.sb_num_analites.value()
        num_teo_plates = self.ui.sb_teo_plates.value()
        max_iters = self.ui.sb_num_iter.value()
        conc_init = np.zeros(num_analites)
        ks_analites = np.zeros(num_analites)

        for i in np.arange(num_analites):
            ks_analites[i] = float(self.ui.tbw_analites_info.item(i, 1).text())
            conc_init[i] = float(self.ui.tbw_analites_info.item(i, 2).text())

        return Model(num_analites, num_teo_plates, max_iters, conc_init, ks_analites, ideal)

    def go_to_transmission(self):
        tras_model = self.collect_model()
        tw = Trasmission(self, tras_model)
        tw.show()

    def go_to_cromatogram(self):
        crom_model = self.collect_model()
        cw = Cromatogram(self, crom_model)
        cw.show()


if __name__ == '__main__':
    import sys
    from PyQt4 import QtGui

    app = QtGui.QApplication(sys.argv)
    main = Main()
    main.show()

    sys.exit(app.exec_())
