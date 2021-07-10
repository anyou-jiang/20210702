import numpy as np
from SkewedSlicingTree import SkewedSlicingTree
from NormPolishExpression import NormPolishExpression
from SlicingTreeSolutionCache import SlicingTreeSolutionCache
import math
import copy
import warnings
import enum
from Utilities import LOG
import statistics
from Parameters import Parameters


# Algorithm 10.4 Wong-Liu Floorplanning (P, e, r, k)
class AnnealingSimulator:
    class TerminateReason(enum.Enum):
        FrozenTemperatureReached = 0
        NeighborsRejectRateTooHigh = 1
        MaxAnnealCountReached = 2
        ToHighHitCacheRate = 3
        EndOfReason = 4

    class PerturbOperation(enum.Enum):
        SwapTwoAdjacentOperands = 0
        InvertChain = 1
        SwapTwoAdjacentOperandsOperators = 2
        EndOfOperation = 3  # always to the last item

    DefaultDeltaAvg = 20

    @staticmethod
    def _randomlySwapTwoAdjacentOperands(expression):
        return expression.randomlySwapTwoAdjacentOperands()

    @staticmethod
    def _InvertChain(expression):
        return expression.randomlyInvertChain()

    @staticmethod
    def _testSwapTwoAdjacentOperandOperator(expression):
        return expression.testSwapTwoAdjacentOperandOperator()

    @staticmethod
    def _testSwapTwoAdjacentOperatorAndOperand(expression):
        return expression.testSwapTwoAdjacentOperatorAndOperand()

    def _satisfyFeatureSpecificConstraints(self, expression):
        return True  # todo: add feature more feature specific constrains

    def selectOperation(self):
        if Parameters.perturbOperationSelectionRule == Parameters.PerturbOperationSelectionRules.Randomly:
            operationInt = np.random.randint(low=0, high=AnnealingSimulator.PerturbOperation.EndOfOperation.value)
            return AnnealingSimulator.PerturbOperation(operationInt)

    def __init__(self):
        self._startExpression = None
        self._minimumDelay = float('inf')
        self._bestShapeSolution = None
        self._bestExpression = None
        self._terminateReason = AnnealingSimulator.TerminateReason.EndOfReason
        self._deltaAvg = AnnealingSimulator.DefaultDeltaAvg

        self._acceptNonSolvableProb = 0.9
        self._acceptNotSatisfiedConstraintProb = 0.9
        self._numIterationPerTemperature = 20
        self._startTemperature = 100
        self._initProbabilityToAcceptUphill = 0.98
        self._temperatureAnnealingRate = 0.85
        self._rejectRatioThreshold = 0.95
        self._hitCacheThreshold = 1
        self._frozenTemperature = 1e-3
        self._maxAnnealingCount = 10
        self._maxNumPerturbToEstDeltaAvg = 500
        self._preferredNumOfPosUphillToEstDeltaAvg = 10

        self._randomSeed = 100

        self._delaySamples = []
        self._delayEvaluationsSamples = []
        self._delayToCacheSamples = []
        self._cacheHitRate = 0

    def appendToCacheSamples(self, sample):
        self._delayToCacheSamples.append(sample)

    def appendtoEvaluationSamples(self, sample):
        self._delayEvaluationsSamples.append(sample)

    def appendDelaySample(self, sample):
        self._delaySamples.append(sample)

    def solutionResult(self):
        return {"bestExpression": self._bestExpression,
                "bestShapes": self._bestShapeSolution,
                "minimumDelay": self._minimumDelay,
                "delayMean": 0 if len(self._delaySamples) < 1 else statistics.mean(self._delaySamples),
                "delayStdVariance": 0 if len(self._delaySamples) < 2 else math.sqrt(
                    statistics.variance(self._delaySamples)),
                "delayMin": 0 if len(self._delaySamples) < 1 else min(self._delaySamples),
                "delayMax": 0 if len(self._delaySamples) < 1 else max(self._delaySamples),
                "cacheHitRate": self._cacheHitRate,
                "terminateReason": self._terminateReason.value}

    def die(self):
        return np.random.random()

    def setTemperatureAnnealingRate(self, temp):
        self._temperatureAnnealingRate = temp

    def setRandomSeed(self, seed):
        self._randomSeed = seed
        np.random.seed(self._randomSeed)

    def setMaxNumPerturbToEstDeltaAvg(self, num):
        self._maxNumPerturbToEstDeltaAvg = num

    def setPreferredNumOfPosUphillToEstDeltaAvg(self, num):
        self._preferredNumOfPosUphillToEstDeltaAvg = num

    def setMaxAnnealingCount(self, count):
        self._maxAnnealingCount = count

    def setRejectRatioThreshold(self, ratio):
        self._rejectRatioThreshold = ratio

    def setFrozenTemperature(self, temperature):
        self._frozenTemperature = temperature

    def setTemperatureAnnealingRate(self, rate):
        self._temperatureAnnealingRate = rate

    def setStartTemperature(self, T):
        self._startTemperature = T

    def setInitProbabilityToAccessUphill(self, prob):
        self._initProbabilityToAcceptUphill = prob

    def setNumIterationPerTemperature(self, maxNum):
        self._numIterationPerTemperature = maxNum

    def getHeuristicDelay(self):
        numOfTask = self._startExpression.numOfTask()
        return (2 + 2 * numOfTask) / 2 * numOfTask  # heuristically 2 + 4 + 8 + ... + 2 * #numOfTask

    def setStartExpression(self, startExpr):
        self._startExpression = NormPolishExpression(startExpr)  # Todo: to check start expression

    def _findNeighborExpression(self, currentExpression):
        operation = self.selectOperation()
        if operation is AnnealingSimulator.PerturbOperation.SwapTwoAdjacentOperands:
            neighborExpression = AnnealingSimulator._randomlySwapTwoAdjacentOperands(currentExpression)
        elif operation is AnnealingSimulator.PerturbOperation.InvertChain:
            neighborExpression = AnnealingSimulator._InvertChain(currentExpression)
        elif operation is AnnealingSimulator.PerturbOperation.SwapTwoAdjacentOperandsOperators:
            # for a special case, 01F2F3F4F..., it has no neighbors by swapping two adjacent operand and operators
            if currentExpression.isFullUnqiueExpression():
                LOG('full unqiue expression found, {}'.format(currentExpression.getExpressionInfoCompactFormat()), 0)
                # try another operation
                return self._findNeighborExpression(currentExpression)
            else:
                done = False
                MAXLOOP = 100
                countLoop = 0
                while (not done) and (countLoop < MAXLOOP):
                    countLoop = countLoop + 1
                    (done, neighborExpression) = AnnealingSimulator._testSwapTwoAdjacentOperandOperator(
                        currentExpression)
                    if not done:
                        (done, neighborExpression) = AnnealingSimulator._testSwapTwoAdjacentOperatorAndOperand(
                            currentExpression)

                if countLoop >= MAXLOOP:
                    LOG(
                        'Max Loop reached when searching for neighbors by swap operand/operator for expression = {}'.format(
                            currentExpression.getExpressionInfoCompactFormat()), 1)
                    # try another operation
                    return self._findNeighborExpression(currentExpression)

        return self._satisfyFeatureSpecificConstraints(neighborExpression), neighborExpression

    def runSimulation(self):
        currentExpression = self._startExpression
        currentDelay = self._minimumDelay
        temperature = -self._deltaAvg / math.log(self._initProbabilityToAcceptUphill)
        annealingCounts = 0
        SlicingTreeSolutionCache.reset()

        while True:
            continueAnnealing = True
            reject = 0
            hitCacheCount = 0
            numOfTreeEvaluate = 0
            for iterCount in range(self._numIterationPerTemperature):
                foundValid = False
                slicingTree = None
                (foundNeighbor, neighborExpression) = self._findNeighborExpression(currentExpression)
                if not self._bestExpression is None:
                    LOG("best exression = {}".format(self._bestExpression.getExpressionInfoCompactFormat()), 1)
                LOG('Next Expr={}'.format(neighborExpression.getExpressionInfoCompactFormat()), 1)
                if foundNeighbor:
                    slicingTree = SkewedSlicingTree(neighborExpression)
                    foundValid = slicingTree.satisfyFeatureSpecificConstraints(Parameters.featureConstrain)
                if foundValid:
                    slicingTree.evaluate()
                    numOfTreeEvaluate = numOfTreeEvaluate + 1
                    hitCache = slicingTree.hitCache()
                    if hitCache:
                        hitCacheCount = hitCacheCount + 1
                    solvable = slicingTree.isSolvable()
                    if solvable:
                        neighborDelay = slicingTree.getMinimumDelay()
                        self.appendDelaySample(neighborDelay)
                        #deltaDelay = neighborDelay - currentDelay
                        deltaDelay = neighborDelay - neighborDelay
                        dieProb = self.die()
                        try:
                            temperatureProb = math.exp(-deltaDelay / temperature)
                        except OverflowError:
                            LOG(' temperatureProb overflow (too big), deltaCost = {}, temperature = {}'.format(
                                deltaDelay, temperature))
                            temperatureProb = 1.0

                        upOrDownHill = 'd' if deltaDelay <= 0 else 'u'
                        bestOrNot = '-'
                        if deltaDelay <= 0 or dieProb < temperatureProb: # find better solution or up-hill climb
                            prevExpression = currentExpression
                            prevDelay = currentDelay
                            currentExpression = copy.deepcopy(neighborExpression)
                            currentDelay = neighborDelay

                            bestOrNot = 'b' if neighborDelay < self._minimumDelay else '-'
                            if neighborDelay < self._minimumDelay: # Find better solution
                                self._minimumDelay = neighborDelay
                                self._bestShapeSolution = copy.deepcopy(slicingTree.getBestShapeSolution())
                                self._bestExpression = copy.deepcopy(neighborExpression)

                            self.LOG_SOLVABLE_BEST_UPDATE(annealingCounts, bestOrNot, dieProb, iterCount,
                                                          neighborDelay,
                                                          neighborExpression, prevDelay, prevExpression,
                                                          slicingTree,
                                                          temperature, temperatureProb, upOrDownHill)

                        else:
                            prevExpression = currentExpression
                            reject = reject + 1
                            self.LOG_SOLVABLE_REJECT(annealingCounts, bestOrNot, currentDelay, dieProb, iterCount,
                                                     neighborDelay,
                                                     neighborExpression, prevExpression, reject, slicingTree,
                                                     temperature,
                                                     temperatureProb, upOrDownHill)
                    else:  # no solvable for neighbor expression
                        dieProb = self.die()
                        temperatureProb = self._acceptNonSolvableProb
                        if dieProb < temperatureProb:
                            prevExpression = currentExpression
                            prevDelay = currentDelay
                            currentExpression = copy.deepcopy(neighborExpression)
                            currentDelay = self.getHeuristicDelay()

                            self.LOG_NOSOLVABLE_UPHILL(annealingCounts, currentDelay, dieProb, iterCount,
                                                       neighborExpression, prevExpression, reject, temperature,
                                                       temperatureProb)
                        else:
                            prevExpression = currentExpression
                            reject = reject + 1
                            self.LOG_NOSOLVABLE_REJECT(annealingCounts, currentDelay, dieProb, iterCount,
                                                       neighborExpression, prevExpression, reject, temperature,
                                                       temperatureProb)

                else:
                    dieProb = self.die()
                    temperatureProb = self._acceptNotSatisfiedConstraintProb
                    if dieProb < temperatureProb:
                        prevExpression = currentExpression
                        prevDelay = currentDelay
                        currentExpression = copy.deepcopy(neighborExpression)
                        currentDelay = self.getHeuristicDelay()
                        self.LOG_NOT_FOUND_VALID_NEIGHBOR(annealingCounts, iterCount, reject, temperature)
                    else:
                        if not foundNeighbor:
                            LOG('{} not found neighbors for expression {}'.format(annealingCounts,
                                                                              currentExpression.getExpressionInfoCompactFormat()))
                        else:
                            LOG('{} expression {} -> neighbor {}, but it is not valid'.format(annealingCounts,
                                                                                          currentExpression.getExpressionInfoCompactFormat(),
                                                                                          neighborExpression.getExpressionInfoCompactFormat()))
                        reject = reject + 1
                        self.LOG_NOT_FOUND_VALID_NEIGHBOR(annealingCounts, iterCount, reject, temperature)

            temperature = temperature * self._temperatureAnnealingRate
            if numOfTreeEvaluate == 0:
                numOfTreeEvaluate = 1
            self._cacheHitRate = (1.0 * hitCacheCount / numOfTreeEvaluate)
            LOG("{} hit cache rate = {:.2f}({}/{}), cacheSize = {}".format(annealingCounts, self._cacheHitRate,
                                                                           hitCacheCount, numOfTreeEvaluate,
                                                                           SlicingTreeSolutionCache.cacheSize()), 0)
            annealingCounts = annealingCounts + 1
            if (1.0 * reject / self._numIterationPerTemperature) > self._rejectRatioThreshold \
                    or temperature < self._frozenTemperature \
                    or annealingCounts > self._maxAnnealingCount \
                    or self._cacheHitRate > self._hitCacheThreshold:
                continueAnnealing = False
                if (1.0 * reject / self._numIterationPerTemperature) > self._rejectRatioThreshold:
                    self._terminateReason = AnnealingSimulator.TerminateReason.NeighborsRejectRateTooHigh
                elif temperature < self._frozenTemperature:
                    self._terminateReason = AnnealingSimulator.TerminateReason.FrozenTemperatureReached
                elif annealingCounts > self._maxAnnealingCount:
                    self._terminateReason = AnnealingSimulator.TerminateReason.MaxAnnealCountReached
                else:
                    self._terminateReason = AnnealingSimulator.TerminateReason.ToHighHitCacheRate
            else:
                continueAnnealing = True
            if not continueAnnealing:
                break

    def LOG_NOT_FOUND_VALID_NEIGHBOR(self, annealingCounts, iterCount, reject, temperature):
        LOG(
            "[{}-{}] A-{}-A-{} Eb:{} Sb:{} Cb:{} "
            "T:{:.2f}, RJ:{}".format(
                annealingCounts, iterCount, '-', '-', "None" if self._bestExpression is None else self._bestExpression.getExpressionInfoCompactFormat(),
                SkewedSlicingTree.packetSolutionInfo(self._bestShapeSolution), self._minimumDelay, temperature,
                reject), 0)

    def LOG_NOSOLVABLE_REJECT(self, annealingCounts, currentDelay, dieProb, iterCount, neighborExpression,
                              prevExpression, reject, temperature, temperatureProb):
        LOG(
            "[{}-{}] A-{}-A-{} Ecnb:[{}][{}][{}] Snb:["
            "{}][{}] Ccnb:[{}][{}][{}] "
            "T:{:.2f}, DP:{:.2f} TP:{:.2f}, RJ:{}".format(
                annealingCounts, iterCount, "!", "-",
                prevExpression.getExpressionInfoCompactFormat(),
                neighborExpression.getExpressionInfoCompactFormat(),
                self._bestExpression.getExpressionInfoCompactFormat(),
                "None",
                SkewedSlicingTree.packetSolutionInfo(self._bestShapeSolution),
                currentDelay, "None", self._minimumDelay,
                temperature, dieProb, temperatureProb, reject), 0)

    def LOG_NOSOLVABLE_UPHILL(self, annealingCounts, currentDelay, dieProb, iterCount, neighborExpression,
                              prevExpression, reject, temperature, temperatureProb):
        LOG(
            "[{}-{}] A-{}-B-{} Ecnb:[{}][{}][{}] Snb:["
            "{}][{}] Ccnb:[{}][{}][{}] "
            "T:{:.2f}, DP:{:.2f} TP:{:.2f}, RJ:{}".format(
                annealingCounts, iterCount, "!", "-",
                prevExpression.getExpressionInfoCompactFormat(),
                neighborExpression.getExpressionInfoCompactFormat(),
                self._bestExpression.getExpressionInfoCompactFormat(),
                "None",
                SkewedSlicingTree.packetSolutionInfo(self._bestShapeSolution),
                currentDelay, "None", self._minimumDelay,
                temperature, dieProb, temperatureProb, reject), 0)

    def LOG_SOLVABLE_REJECT(self, annealingCounts, bestOrNot, currentDelay, dieProb, iterCount, neighborDelay,
                            neighborExpression, prevExpression, reject, slicingTree, temperature, temperatureProb,
                            upOrDownHill):
        LOG(
            "[{}-{}] A-{}-A-{} Ecnb:[{}][{}][{}] Snb:["
            "{}][{}] Ccnb:[{}][{}][{}] "
            "T:{:.2f}, DP:{:.2f}, TP:{:.2f}, RJ:{}".format(
                annealingCounts, iterCount, upOrDownHill, bestOrNot,
                prevExpression.getExpressionInfoCompactFormat(),
                neighborExpression.getExpressionInfoCompactFormat(),
                self._bestExpression.getExpressionInfoCompactFormat(),
                SkewedSlicingTree.packetSolutionInfo(slicingTree.getBestShapeSolution()),
                SkewedSlicingTree.packetSolutionInfo(self._bestShapeSolution),
                currentDelay, neighborDelay, self._minimumDelay,
                temperature, dieProb, temperatureProb, reject), 0)

    def LOG_SOLVABLE_BEST_UPDATE(self, annealingCounts, bestOrNot, dieProb, iterCount, neighborDelay,
                                 neighborExpression,
                                 prevDelay, prevExpression, slicingTree, temperature, temperatureProb, upOrDownHill):
        LOG(
            "[{}-{}] A-{}-B-{} Ecnb:[{}][{}][{}] Snb:[{}][{}] Ccnb:[{}][{}][{}] "
            "T:{:.2f}, DP:{:.2f}, TP:{:.2f}".format(
                annealingCounts, iterCount, upOrDownHill, bestOrNot,
                prevExpression.getExpressionInfoCompactFormat(),
                neighborExpression.getExpressionInfoCompactFormat(),
                self._bestExpression.getExpressionInfoCompactFormat(),
                SkewedSlicingTree.packetSolutionInfo(slicingTree.getBestShapeSolution()),
                SkewedSlicingTree.packetSolutionInfo(self._bestShapeSolution),
                prevDelay, neighborDelay, self._minimumDelay,
                temperature, dieProb, temperatureProb), 0)
