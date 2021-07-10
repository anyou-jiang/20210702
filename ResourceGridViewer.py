import numpy as np
import matplotlib.pyplot as plt
from SoftModuleInfo import SoftModuleInfo
import copy
from Utilities import LOG
import math


class ResourceGridViewer:

    def drawAndSaveResourceGridBySolution(self, solution, filePath):
        hmax = solution["h"] + 1
        wmax = solution["w"] + 1
        Z = np.ones((hmax, wmax))
        x = np.arange(-0.5, wmax, 1)
        y = np.arange(-0.5, hmax, 1)
        startDays = solution['s']
        startPersons = solution['f']
        ids = solution['id']
        numOfTasks = solution['n']
        startPerson = 0
        centers = {}
        for (startDay, startPerson, id) in zip(startDays, startPersons, ids):
            shape = SoftModuleInfo.getShapeInfoById(id)
            numDay = shape['w']
            numPerson = shape['h']
            task_Id = int(id.split("-")[0])
            centers[task_Id] = (startDay + numDay * 1.0 / 2 - 0.5, startPerson + numPerson * 1.0 / 2 - 0.5)
            for day in range(numDay):
                for person in range(numPerson):
                    dayOffset = startDay + day
                    personOffset = startPerson + person
                    Z[personOffset, dayOffset] = 1 / numOfTasks * task_Id

        fig, ax = plt.subplots()
        ax.pcolormesh(x, y, Z, cmap='terrain')
        ax.set_xticks([x for x in range(wmax)])
        ax.set_yticks([x for x in range(0, hmax, 2)] + [hmax - 1])
        for x in range(wmax):
            ax.plot([x + 0.5, x + 0.5], [0, hmax - 0.5], linestyle='--', color='grey')
        ax.plot([-0.5, wmax - 0.5], [hmax - 0.5, hmax - 0.5], linestyle='--',
                color='grey')
        ax.set_xlabel('Days')
        ax.set_ylabel('Persons')
        ax.text(0, hmax,
                'solution info: n={},w={},h={},d={}'.format(solution['n'], solution['w'], solution['h'], solution['d']))
        for key in centers.keys():
            ax.text(centers[key][0], centers[key][1], "{}-{}".format((key//4)+1, (key % 4) + 1), verticalalignment='center',
                    horizontalalignment='center')
        # plt.show()
        fig.savefig(filePath)
        plt.close()


