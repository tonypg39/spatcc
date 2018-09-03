__author__ = 'Toni'

import math
import numpy as np


class Model():
    def __init__(self, num_analites, num_teo_plates, max_iter, conc_initial, ks_analites, ideal_type=True):
        # Static parameters of the class

        self.num_analites = num_analites
        self.num_teo_plates = num_teo_plates
        self.max_iter = max_iter
        # Chemical properties
        self.conc_initial = conc_initial
        self.ks_analites = ks_analites
        self.is_ideal_type = ideal_type

        # Dynamic Simulation parameters

        conc_total = np.zeros((self.num_analites, self.num_teo_plates))
        conc_FE_eq = np.zeros((self.num_analites, self.num_teo_plates))
        conc_FE_mov = np.zeros((self.num_analites, self.num_teo_plates))
        conc_FM_eq = np.zeros((self.num_analites, self.num_teo_plates))
        conc_FM_mov = np.zeros((self.num_analites, self.num_teo_plates))

        self.current_state = (conc_total, conc_FE_eq, conc_FE_mov, conc_FM_eq, conc_FM_mov)
        self.count_iter = 0
        self.finished = False

    def update(self, steps):
        """
        This method updates the value of current_state and takes one step further the
        computations of the respective concentration of the analites.
        """
        if self.count_iter >= self.max_iter:
            return

        cant_plates = self.num_teo_plates

        n_analitos = self.num_analites
        ideal_type = self.is_ideal_type
        iters = steps
        fFM = np.zeros(n_analitos)
        fFE = np.zeros(n_analitos)
        ks_analitos = self.ks_analites

        conc_total, conc_FE_eq, conc_FE_mov, conc_FM_eq, conc_FM_mov = self.current_state

        if self.count_iter == 0:
            conc_FM_eq[:, .0] = self.conc_initial

        for i in np.arange(n_analitos):
            fFE[i] = ks_analitos[i] / (ks_analitos[i] + 1)
            fFM[i] = 1 - fFE[i]

        k = 0
        while k < iters:
            if ideal_type:
                for i in np.arange(n_analitos):
                    for j in np.arange(cant_plates):
                        aux = conc_FE_eq[i][j] + conc_FM_eq[i][j]
                        conc_FE_eq[i, j] = fFE[i] * aux
                        conc_FM_eq[i, j] = fFM[i] * aux
            else:
                for i in np.arange(n_analitos):
                    for j in np.arange(cant_plates):
                        aux = conc_FE_eq[i][j] + conc_FM_eq[i][j]
                        conc_FE_eq[i, j] = conc_FM_eq[i, j] * ks_analitos[i] / (conc_FM_eq[i, j] * ks_analitos[i] + 1)
                        conc_FM_eq[i, j] = (aux * ks_analitos[i] - ks_analitos[i] - 1 + math.sqrt(
                            (aux * ks_analitos[i] - ks_analitos[i] - 1) ** 2 + 4 * aux * ks_analitos[i])) / (
                                               2 * ks_analitos[i])

            for i in np.arange(n_analitos):
                for j in np.arange(cant_plates):
                    conc_FE_mov[i, j - 1] = conc_FE_eq[i, j - 1]
                    conc_FM_mov[i, j] = conc_FM_eq[i, j - 1]

                conc_FM_mov[i, 0] = 0

            for i in np.arange(n_analitos):
                for j in np.arange(cant_plates):
                    conc_total[i][j] = conc_FE_mov[i][j] + conc_FM_mov[i][j]

            for i in np.arange(n_analitos):
                for j in np.arange(cant_plates):
                    conc_FE_eq[i][j] = conc_FE_mov[i][j]
                    conc_FM_eq[i][j] = conc_FM_mov[i][j]

            k += 1
            self.count_iter += 1
            if self.count_iter >= self.max_iter:
                self.finished = True

        self.current_state = conc_total, conc_FE_eq, conc_FE_mov, conc_FM_eq, conc_FM_mov
