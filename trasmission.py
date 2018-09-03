__author__ = 'Toni'

import numpy as np
import numpy.random as rnd
from PyQt4.QtCore import QString, QTimer, Qt
from PyQt4.QtGui import *
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from matplotlibwidget import MatplotlibWidget
from tras_w import Ui_TrasmissionWindow
import math

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


class Trasmission(QMainWindow):
    def __init__(self, parent, tmodel):
        QMainWindow.__init__(self, parent)
        self.ui = Ui_TrasmissionWindow()
        self.ui.setupUi(self)
        self.tmodel = tmodel

        # Initialize the matplotlib window and the toolbar
        self.mpl_window = MatplotlibWidget()
        self.ui.verticalLayout_2.addWidget(self.mpl_window)
        self.toolbar = NavigationToolbar(self.mpl_window, self)
        self.ui.verticalLayout_2.addWidget(self.toolbar)

        # Initialize the color column
        self.color_list = generate_colors(self.tmodel.num_analites)
        self.color_col = ColorColumn(self.ui.wid_column, self.tmodel.num_teo_plates,
                                     self.tmodel.num_analites, self.color_list,
                                     self.tmodel.current_state[0], 380, 300)

        # Simulation
        self.timer = QTimer()
        self.timer.timeout.connect(self.timeout)
        self.ui.pb_exec.clicked.connect(self.start_stop)
        self.running = False

    def start_stop(self):
        if self.running:
            self.running = False
            self.timer.stop()
            self.ui.pb_exec.setText("Ejecutar")

        else:  # not running now
            self.running = True
            self.timer.start()
            self.ui.pb_exec.setText("Detener")

    def timeout(self):
        self.tmodel.update(1)
        temp = self.tmodel.current_state[0].copy()
        self.color_col.update_conc(temp, (self.tmodel.count_iter < 10))
        self.color_col.repaint()
        self.plot()
        if self.tmodel.finished:
            self.timer.stop()

    def plot(self):
        self.mpl_window.axes.hold(False)
        self.mpl_window.axes.axis = ([1, self.tmodel.num_teo_plates, 0, 100])
        x = np.linspace(0, self.tmodel.num_teo_plates, self.tmodel.num_teo_plates)
        y = self.tmodel.current_state[0]

        for i in np.arange(self.tmodel.num_analites):
            self.mpl_window.axes.set_xlabel(_translate("Numero de platos teoricos", "Numero de platos teoricos", None))
            self.mpl_window.axes.set_ylabel(_translate("Intensidad de la senal", "Intensidad de la senal", None))
            self.mpl_window.axes.plot(x, y[i], color2str(self.color_list[i]), label=str(chr(65 + i)))
            self.mpl_window.axes.hold(True)

        self.mpl_window.axes.grid()
        self.mpl_window.axes.legend()
        self.mpl_window.draw()


class ColorColumn(QWidget):
    def __init__(self, parent, num_teo_plates, num_analites, color_list, init_conc, height=250, width=150):
        QWidget.__init__(self, parent)
        self.num_plates = num_teo_plates
        self.num_analites = num_analites
        self.color_list = color_list
        self.intensity = init_conc
        self.max_intensity = 0.0
        self.normalize_conc()
        self.margin = 30
        self.setGeometry(22, 0, width, height)
        print 'Total Height: ' + str(self.height())
        print 'Number of plates: ' + str(self.num_plates)
        self.show()

    def normalize_conc(self, set_max_conc=False):
        if set_max_conc:
            self.max_intensity = np.max(self.intensity)
        if self.max_intensity > 1e-3:
            self.intensity /= self.max_intensity

    def update_conc(self, norm_conc, set_max_conc=False):
        self.intensity = norm_conc
        self.normalize_conc(set_max_conc)

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        # Setting the background color
        qp.fillRect(0, 0, 120, self.height() + 15, QBrush(QColor(45, 45, 25)))

        target_size = (self.height() - self.margin)
        plate_height = 1
        if self.num_plates >= target_size:
            intensity_field = pool(self.intensity, target_size)
        else:
            intensity_field = expand(self.intensity, target_size)

        for i in np.arange(intensity_field.shape[1]):
            color = combine(self.color_list, intensity_field[:, i])
            qp.fillRect(10, i * plate_height + 10, 100, plate_height, QBrush(color))
        qp.end()


def combine(colors, intense):
    """
    :return: The addition of both colors
    """
    c = QColor()
    l = len(colors)
    r, g, b = 0, 0, 0
    s = np.sum(intense)
    if s == 0:
        return QColor(255, 255, 255)

    for i in range(l):
        r += min(255, colors[i][0] * (intense[i] / s))
        g += min(255, colors[i][1] * (intense[i] / s))
        b += min(255, colors[i][2] * (intense[i] / s))

    rx, gx, bx = int(r / l), int(g / l), int(b / l)
    mx = max(intense)
    # r = int(255 - (255 - int(r / l)) * max(intense))
    # g = int(255 - (255 - int(g / l)) * max(intense))
    # b = int(255 - (255 - int(b / l)) * max(intense))
    r = eval_color(rx, mx)
    g = eval_color(gx, mx)
    b = eval_color(bx, mx)
    c.setRed(r)
    c.setGreen(g)
    c.setBlue(b)
    return c


def eval_color(cx, ci):
    b = math.log(1 / (255.0 - cx + 1))
    y = (255 - cx + 1) * math.exp(b * ci) + cx - 1
    return int(y)


def generate_colors(n):
    c = []
    for i in np.arange(1, n + 1):
        b = np.array([(i & (1 << j)) > 0 for j in np.arange(3)])
        c.append(((i / 8 + 1) * 90) % 200 * b)
    return c


def color2str(col):
    s = "#"
    cs = [int(col[i]) for i in range(3)]
    for i in cs:
        if i > 15:
            s += hex(i)[2:]
        else:
            s += '0' + hex(i)[2:]
    return s


def expand(smaller, bigger_size):
    """
    Expands the smaller array in the second dimension
    """
    smaller_size = smaller.shape[1]
    k = bigger_size / smaller_size
    bigger = np.ones((smaller.shape[0], bigger_size))
    r = bigger_size % smaller_size
    count_extra = 0
    step_for_extra = smaller_size
    if r != 0:
        step_for_extra /= r

    for i in np.arange(smaller_size):
        for j in np.arange(smaller.shape[0]):
            if ((i + 1) % step_for_extra == 0) and count_extra < r:
                st = k * i + count_extra
                fn = st + k + 1
                # print smaller[j][i]
                bigger[j][st:fn] = smaller[j][i]
                if j == smaller.shape[0] - 1:
                    count_extra += 1
            else:
                st = k * i + count_extra
                fn = st + k
                # print smaller[j][i]
                bigger[j][st:fn] = smaller[j][i]
    return bigger


def pool(bigger, smaller_size):
    """
    Pools down the bigger array in the second dimension
    """
    bigger_size = bigger.shape[1]
    k = bigger_size / smaller_size
    smaller = np.ones((bigger.shape[0], smaller_size))
    r = bigger_size % smaller_size
    count_extra = 0
    step_for_extra = smaller_size
    if r != 0:
        step_for_extra /= r

    for i in np.arange(smaller_size):
        for j in np.arange(bigger.shape[0]):
            if ((i + 1) % step_for_extra == 0) and count_extra < r:
                st = k * i + count_extra
                fn = st + k + 1
                smaller[j][i] = np.average(bigger[j][st:fn])
                if j == smaller.shape[0] - 1:
                    count_extra += 1
            else:
                st = k * i + count_extra
                fn = st + k
                smaller[j][i] = np.average(bigger[j][st:fn])
    return smaller
