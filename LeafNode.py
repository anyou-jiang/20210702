from TreeNode import TreeNode
from Utilities import overrides
from SoftModuleInfo import SoftModuleInfo


class LeafNode(TreeNode):

    def __init__(self, tag, tree):
        super(LeafNode, self).__init__(tag, tree)

    @overrides(TreeNode)
    def getNumOfShapeToEvaluate(self):
        return 0

    @overrides(TreeNode)
    def getNumOfShapeToCache(self):
        return 0

    @overrides(TreeNode)
    def postTraversal(self, func):
        func(self.nodeTag)
        if self.shapes is not None:
            if len(self.shapes) == 0:
                func("{}")
            else:
                for shape in self.shapes:
                    func(shape)

    @overrides(TreeNode)
    def evaluateShapes(self):
        if self.shapes is None:
            self.shapes = SoftModuleInfo.getModuleInfoByTag(self.nodeTag)
        return self.shapes

    @overrides(TreeNode)
    def getNumOfShapeToCachePerNode(self):
        return '{}-'.format(len(self.shapes))

