from NodeTag import NodeTag
from LeafNode import LeafNode
from InternalNode import InternalNode
from collections import deque
from SlicingTreeSolutionCache import SlicingTreeSolutionCache
from Parameters import Parameters

import statistics
import math
import sys
from SoftModuleInfo import SoftModuleInfo


class SkewedSlicingTree:

    @staticmethod
    def fullExpression(tree):
        return tree.getExpression()

    @staticmethod
    def compactFInTree(tree):
        treeRoot = tree.root()
        (isLeaf, compactTreeRoot) = SkewedSlicingTree.compactF(treeRoot)
        postTreeExpression = []

        def appendTag(tag):
            postTreeExpression.append(tag)

        if isLeaf:
            return tuple(compactTreeRoot.nodeTag)
        else:
            compactTreeRoot.postTraversal(appendTag)
            return tuple(postTreeExpression)

    @staticmethod
    def compactF(node):
        if isinstance(node, LeafNode):
            return True, LeafNode((node.nodeTag, ), None)
        elif NodeTag.isT(node.nodeTag):
            (isLeafLeft, left) = SkewedSlicingTree.compactF(node.leftNode())
            (isLeafRight, right) = SkewedSlicingTree.compactF(node.rightNode())
            compactNode = InternalNode('T', left, right, None)
            return False, compactNode
        else:
            (isLeafLeft, left) = SkewedSlicingTree.compactF(node.leftNode())
            (isLeafRight, right) = SkewedSlicingTree.compactF(node.rightNode())
            if isLeafLeft and isLeafRight:
                tag = list(left.nodeTag) + list(right.nodeTag)
                tag.sort()
                return True, LeafNode(tuple(tag), None)
            else:
                return False, InternalNode('F', left, right, None)

    @staticmethod
    def packetSolutionInfo(solutionDict):
        if solutionDict is None:
            return 'no-solution'
        return "n{}w{}h{}d{}wd{}s:{}f:{}id:{}".format(solutionDict["n"], solutionDict["w"], solutionDict["h"], solutionDict["d"], solutionDict["wd"],
                                          ''.join(str(solutionDict["s"])),
                                          ''.join(str(solutionDict["f"])),
                                          ','.join(solutionDict["id"]))

    class TreeNodeStack:
        def __init__(self):
            self._stack = deque()

        def push(self, treeNode):
            self._stack.append(treeNode)

        def pop(self):
            if len(self._stack) <= 0:
                raise IndexError('Popping a stack out of bound')
                return None
            else:
                return self._stack.pop()

    def __init__(self, expression):  # input: NormalPolishExpression
        self._expression = expression
        self._polishExpressionEvaluation()
        self._bestShapeSolution = None
        self._solvable = False
        self._hitCache = False
        self._numOfPendingT = 0

    def getExpression(self):
        return self._expression

    def CheckTaskPrecedence(self):
        self.evaluate()
        if not self.isSolvable():
            return False

        num_of_task = self._bestShapeSolution["n"]
        task_id_pos = {}
        for task_id in range(num_of_task):
            id = "{}-0".format(task_id)
            task_id_pos[task_id] = self._bestShapeSolution['id'].index(id)

        # calculate the completion time of the task
        start_days = self._bestShapeSolution["s"]
        completion_days = start_days.copy()

        for task_id in range(num_of_task):
            start = start_days[task_id_pos[task_id]]
            shape = SoftModuleInfo.getShapeInfoById(self._bestShapeSolution['id'][task_id_pos[task_id]])
            day = shape["w"]
            completion_days[task_id_pos[task_id]] += day

        # Task 0 needs to complete before the Task 0 on the next unit.
        for task_id in range(0, num_of_task, 4):

            start_day = start_days[task_id_pos[task_id]]
            complete_day = completion_days[task_id_pos[task_id]]
            for task_id_other in range(0, num_of_task, 4):
                if task_id == task_id_other:
                    continue
                start_day_other = start_days[task_id_pos[task_id_other]]
                if start_day_other >= start_day and start_day_other < complete_day: # confliction between Task0 of different units
                    return False

        # Task 0 needs to be completed before Task 1, Task 2, and Task 3 in the same unit.
        num_of_unit = num_of_task // 4
        for unit in range(num_of_unit):
            start_days_within_unit = [start_days[task_id_pos[4 * unit + i]] for i in range(4)]
            complete_days_task_0 = completion_days[task_id_pos[4 * unit]]
            for task_in_unit in range(1, 4):
                start_day_other_task = start_days_within_unit[task_in_unit]
                if start_day_other_task < complete_days_task_0:
                    return False

        return True


    def satisfyFeatureSpecificConstraints(self, constrain):
        if constrain == Parameters.FeatureConstrains.ENoConstrain:
            return True
        elif constrain == Parameters.FeatureConstrains.ETaskPrecedence:
            return self.CheckTaskPrecedence()

        return False

    def hitCache(self):
        return self._hitCache

    def isNumOfPendingTZero(self):
        return self._numOfPendingT == 0

    def increaseNumOfPendingT(self):
        self._numOfPendingT = self._numOfPendingT + 1

    def decreaseNumOfPendingT(self):
        self._numOfPendingT = self._numOfPendingT - 1

    def isSolvable(self):
        return self._solvable

    def root(self):
        return self._root

    def _polishExpressionEvaluation(self):
        treeNodeStack = self.TreeNodeStack()
        for tag in self._expression:
            # print(tag)
            if NodeTag.isOperand(tag):
                treeNodeStack.push(LeafNode(tag, self))
            elif NodeTag.isOperator(tag):
                right = treeNodeStack.pop()
                left = treeNodeStack.pop()
                treeNodeStack.push((InternalNode(tag, left, right, self)))

        self._root = treeNodeStack.pop()

    def getNumOfShapeToCacheInEachNode(self):
        if self._hitCache:
            return 0
        else:
            return self._root.getNumOfShapeToCachePerNode()

    def getStatisticsOfNumShapeCachePerNode(self):
        if self._hitCache:
            return {"max": 0, "mean": 0, "var": 0}
        else:
            cachePerNode = self._root.getNumOfShapeToCachePerNode()
            cacheNums = [int(x) for x in cachePerNode.split("-") if len(x) > 0]
            return {"max": max(cacheNums), "mean": statistics.mean(cacheNums),
                    "var": math.sqrt(statistics.variance(cacheNums))}

    def getBestShapeSolution(self):
        return self._bestShapeSolution

    def getBestShapeSolutionInfo(self):
        return str(self._bestShapeSolution)

    def getMinimumDelay(self):
        if self._solvable:
            if Parameters.toUseWeightedDelayAsCost:
                return self._bestShapeSolution["wd"]
            else:
                return self._bestShapeSolution["d"]
        else:
            return None

    def getNumOfShapeToCache(self):
        if self._hitCache:
            return 0
        else:
            return self._root.getNumOfShapeToCache()

    def getNumOfShapeToEvaluate(self):
        if self._hitCache:
            return 0
        else:
            return self._root.getNumOfShapeToEvaluate()

    def evaluate(self):
        treeExpression = SkewedSlicingTree.fullExpression(self)
        (cached, cachedSolution) = SlicingTreeSolutionCache.fetchCache(treeExpression)
        if not cached:
            self._hitCache = False
            ShapeSolutions = self._root.evaluateShapes()
            if len(ShapeSolutions) > 0:
                self._solvable = True
                self._bestShapeSolution = ShapeSolutions[0]
            else:
                self._solvable = False
                self._bestShapeSolution = None
            SlicingTreeSolutionCache.addCache(treeExpression, self._bestShapeSolution)
        else:
            self._hitCache = True
            # print('HIT Cache {}'.format(SlicingTreeSolutionCache.hitCachedCount))
            SlicingTreeSolutionCache.hitCachedCount = SlicingTreeSolutionCache.hitCachedCount + 1
            self._bestShapeSolution = cachedSolution
            if self._bestShapeSolution is None:
                self._solvable = False

    def print(self):
        def printFollowedByComma(x):
            print('{},'.format(x))

        self._root.postTraversal(printFollowedByComma)

    def plotFirstNth(self, nth):
        pass  # todo
