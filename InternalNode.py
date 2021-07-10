from TreeNode import TreeNode
from Utilities import overrides, LOG
from NodeTag import NodeTag
from SoftModuleInfo import SoftModuleInfo
from SLIV import SLIV
import copy
from Parameters import Parameters


class InternalNode(TreeNode):

    def __init__(self, tag, leftNode, rightNode, tree):
        super(InternalNode, self).__init__(tag, tree)
        self._leftNode = leftNode
        self._rightNode = rightNode
        self.numOfShapeCombination = 0

    def leftNode(self):
        return self._leftNode

    def rightNode(self):
        return self._rightNode

    @overrides(TreeNode)
    def getNumOfShapeToEvaluate(self):
        return self.numOfShapeCombination + self._leftNode.getNumOfShapeToEvaluate() + self._rightNode.getNumOfShapeToEvaluate()

    @overrides(TreeNode)
    def getNumOfShapeToCache(self):
        return len(self.shapes) + self._leftNode.getNumOfShapeToCache() + self._rightNode.getNumOfShapeToCache()

    @overrides(TreeNode)
    def postTraversal(self, func):
        self._leftNode.postTraversal(func)
        self._rightNode.postTraversal(func)
        func(self.nodeTag)
        if self.shapes is not None:
            if len(self.shapes) == 0:
                func("{}")
            else:
                for shape in self.shapes:
                    func(shape)

    @overrides(TreeNode)
    def evaluateShapes(self):
        leftShapes = self._leftNode.evaluateShapes()
        if NodeTag.isT(self.nodeTag):
            self.rightEnterFromNodeT()
        rightShapes = self._rightNode.evaluateShapes()
        if NodeTag.isT(self.nodeTag):
            self.rightReturnFromNodeT()
        self.numOfShapeCombination = len(leftShapes) * len(rightShapes)
        shapes = []
        # combine shapes according to tag
        if NodeTag.isF(self.nodeTag):
            for left in leftShapes:
                for right in rightShapes:
                    shape = dict()
                    shape["n"] = left["n"] + right["n"]
                    shape["w"] = max(left["w"], right["w"])
                    shape["h"] = left["h"] + right["h"]
                    shape["d"] = left["d"] + right["d"]
                    sminLeft = min(left["s"])
                    sminRight = min(right["s"])
                    assert(sminLeft == sminRight)
                    shape["s"] = left["s"] + right["s"]
                    shape["id"] = left["id"] + right["id"]
                    fminLeft = min(left["f"])
                    fminRight = min(right["f"])
                    assert(fminLeft == fminRight)
                    startOfRight = fminLeft + left["h"]
                    shape["f"] = left["f"] + [y + startOfRight for y in right["f"]]
                    self.calculateWeightedDelay(shape)
                    if shape["h"] <= SoftModuleInfo.Hmax:
                        shapes.append(shape)
        elif NodeTag.isT(self.nodeTag):
            for left in leftShapes:
                for right in rightShapes:
                    shape = dict()
                    shape["n"] = left["n"] + right["n"]
                    shape["w"] = left["w"] + right["w"]
                    shape["h"] = max(left["h"], right["h"])
                    shape["d"] = left["d"] + left["w"] * right["n"] + right["d"]
                    sminLeft = min(left["s"])
                    sminRight = min(right["s"])
                    assert(sminLeft == sminRight)
                    startOfRight = sminLeft + left["w"]
                    shape["s"] = left["s"] + [x + startOfRight for x in right["s"]]
                    shape["id"] = left["id"] + right["id"]
                    shape["f"] = left["f"] + right["f"]
                    self.calculateWeightedDelay(shape)
                    if shape["w"] <= SoftModuleInfo.Wmax:
                        shapes.append(shape)

        # remove none-SLIV supported format
        shapesWithSLIV = []
        if self.canStartPosBeFixed():
            LOG("DEBUG: start pos fixed at node {}".format(self.nodeTag), 0)
            for shape in shapes:
                allShapesAllowed = True
                for startSymb, id in zip(shape["s"], shape["id"]):
                    shapeInfo = SoftModuleInfo.getShapeInfoById(id)
                    numOfSym = shapeInfo["w"]
                    assert(len(shapeInfo["s"]) == 1)
                    if not SLIV.isAllowedSLIV(startSymb, numOfSym):
                        LOG("SLIV banned {} because of shapeInfo = {}, SLIV=({}, {})".format(shape, shapeInfo, startSymb, numOfSym), 0)
                        allShapesAllowed = False
                if allShapesAllowed:
                    shapesWithSLIV.append(shape)

        else:
            LOG("DEBUG: start pos not fixed at node {}".format(self.nodeTag), 0)
            shapesWithSLIV = copy.deepcopy(shapes)

        shapesAfterPrune = copy.deepcopy(shapesWithSLIV)
        if Parameters.toUseWeightedDelayAsCost:
            shapesAfterPrune.sort(key=lambda item: item['wd'])
        else:
            shapesAfterPrune.sort(key=lambda item: item['d'])
        indexHeader = 0
        while indexHeader < len(shapesAfterPrune):
            shapeHeader = shapesAfterPrune[indexHeader]
            indexForward = indexHeader + 1
            while indexForward < len(shapesAfterPrune):
                shapeForward = shapesAfterPrune[indexForward]
                if shapeForward['w'] >= shapeHeader['w'] and shapeForward['h'] >= shapeHeader['h']:
                    shapesAfterPrune.pop(indexForward)  # remove the redundant item but keep forward index in the same place
                else:
                    indexForward = indexForward + 1

            indexHeader = indexHeader + 1

        if len(shapesAfterPrune) == 0:
            LOG("WARNING: no shapes at node tag {}".format(self.nodeTag), 0)
        else:
            LOG("DEBUG: {} shapes at node tag {}".format(len(shapesAfterPrune), self.nodeTag), 0)

        self.shapes = shapesAfterPrune
        return self.shapes

    def calculateWeightedDelay(self, shape):
        # update the weighted delay
        weightedDelay = 0
        for (startSymb, shapeId) in zip(shape["s"], shape["id"]):
            shapeInfo = SoftModuleInfo.getShapeInfoById(shapeId)
            width = shapeInfo["w"]
            ueId = int(shapeId.split("-")[0])
            weight = SoftModuleInfo.ueWeights[ueId]
            weightedDelay = weightedDelay + weight * (startSymb + width)
        shape["wd"] = weightedDelay

    @overrides(TreeNode)
    def getNumOfShapeToCachePerNode(self):
        return self._leftNode.getNumOfShapeToCachePerNode() \
               + self._rightNode.getNumOfShapeToCachePerNode() + '{}-'.format(len(self.costs))
