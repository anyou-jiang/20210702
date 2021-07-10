from SkewedSlicingTree import SkewedSlicingTree
from AnnealingSimulator import AnnealingSimulator
from SoftModuleInfo import SoftModuleInfo
from Utilities import LOG
from SlicingTreeSolutionCache import SlicingTreeSolutionCache
from ResourceGridViewer import ResourceGridViewer
from Parameters import Parameters


init_slicingPattern = "T"
num_unit = 3
num_task_per_unit = 4

maxAnnealingCount = 100
numIterationPerTemperature = 100
temperatureAnnealingRate = 0.99  # 1: no annealing
startTemperature = 100
numOfSim = Parameters.simCount

task_ids = [x for x in range(num_task_per_unit * num_unit)]

basic_task_shapes = [
    {"n": 1, "w": 5, "h": 6, "d": 5, "wd": 0, "s": [0], "f": [0], "id": ["0-0"]},
    {"n": 1, "w": 2, "h": 3, "d": 2, "wd": 0, "s": [0], "f": [0], "id": ["0-1"]},
    {"n": 1, "w": 6, "h": 3, "d": 6, "wd": 0, "s": [0], "f": [0], "id": ["0-2"]},
    {"n": 1, "w": 5, "h": 3, "d": 5, "wd": 0, "s": [0], "f": [0], "id": ["0-3"]}]

Hmax_per_unit = 0
Wmax_per_unit = 0
for basic_shape in basic_task_shapes:
    Hmax_per_unit += basic_shape["h"]
    Wmax_per_unit += basic_shape["w"]

Hmax = Hmax_per_unit * num_unit
Wmax = Wmax_per_unit * num_unit

shapeInfoMap = []
task_weights = {}
for unit_id in range(num_unit):
    for task_id_within_unit in range(num_task_per_unit):
        task_shape = basic_task_shapes[task_id_within_unit].copy()
        task_id = unit_id * 4 + task_id_within_unit
        task_shape["id"] = ["{}-{}".format(task_id, 0)]
        task_weights[task_id] = 1.0
        shapeInfoMap.append([task_shape])

SoftModuleInfo.setInfoMap(shapeInfoMap)
SoftModuleInfo.setUeWeights(task_weights)

SoftModuleInfo.setHmax(Hmax)
SoftModuleInfo.setWmax(Wmax)
LOG(SoftModuleInfo.getInfoMapLog(), 1)

# expressions = [0]
# for nodeIndex in range(1, num_task_per_unit * num_unit):
#     expressions.append(nodeIndex)
#     expressions.append(init_slicingPattern)

expressions = []
for unit in range(num_unit):
    expressions.append(4*unit)
    expressions.append(4*unit+1)
    expressions.append(4*unit+2)
    expressions.append("F")
    expressions.append(4*unit+3)
    expressions.append("F")
    expressions.append("T")
    if unit > 0:
        expressions.append("T")

simulator = AnnealingSimulator()
#simulator.setRandomSeed(1)
simulator.setTemperatureAnnealingRate(temperatureAnnealingRate)
simulator.setStartTemperature(startTemperature)
simulator.setMaxAnnealingCount(maxAnnealingCount)
simulator.setNumIterationPerTemperature(numIterationPerTemperature)
simulator.setStartExpression(expressions)
LOG("Start to run SA simulator from expression = {}".format(expressions), 1)
simulator.runSimulation()

finalSolution = simulator.solutionResult()
LOG('Slicing Tree = {}'.format(finalSolution["bestExpression"].getExpressionInfoCompactFormat()), 1)
LOG('bestShapes = {}'.format(SkewedSlicingTree.packetSolutionInfo(finalSolution["bestShapes"])), 1)
LOG('minimum delay = {}'.format(finalSolution["minimumDelay"]), 1)
LOG('delayMean= {}'.format(finalSolution["delayMean"]), 1)
LOG('delayStdVariance = {}'.format(finalSolution["delayStdVariance"]), 1)
LOG('delayMin = {}'.format(finalSolution["delayMin"]), 1)
LOG('delayMax = {}'.format(finalSolution["delayMax"]), 1)
LOG('terminateReason = {}'.format(AnnealingSimulator.TerminateReason(finalSolution["terminateReason"])), 1)
LOG('cache size = {}'.format(SlicingTreeSolutionCache.cacheSize()), 1)
LOG('cacheHitRate = {}'.format(finalSolution["cacheHitRate"]), 1)

rgv = ResourceGridViewer()
bestSolution = finalSolution["bestShapes"]

if not bestSolution is None:
    pngFileName = 'best_task_schedule_grid.png'
    rgv.drawAndSaveResourceGridBySolution(bestSolution, pngFileName)
