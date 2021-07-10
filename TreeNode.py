
class TreeNode:

    def __init__(self, nodeTag, tree):
        self.nodeTag = nodeTag
        self.shapes = None
        self.tree = tree

    def rightEnterFromNodeT(self):
        self.tree.increaseNumOfPendingT()

    def rightReturnFromNodeT(self):
        self.tree.decreaseNumOfPendingT()

    def canStartPosBeFixed(self):
        return self.tree.isNumOfPendingTZero()

    def postTraversal(self):
        pass

    def evaluateShapes(self):
        pass

    def getNumOfShapeToCache(self):
        pass

    def getNumOfShapeToCachePerNode(self, infoString):
        pass

    def getNumOfShapeToEvaluate(self):
        pass
