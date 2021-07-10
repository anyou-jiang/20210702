import enum
from InternalNode import InternalNode
from LeafNode import LeafNode
from NodeTag import NodeTag


class TreeHash:

    class HashKeyDefinitions(enum.Enum):
        PerTGroup = 0


    hashKeyDefinition = HashKeyDefinitions.PerTGroup




    @staticmethod
    def hash(tree):
        if TreeHash.hashKeyDefinition == TreeHash.HashKeyDefinitions.PerTGroup:
            if NodeTag.isT(tree.root.nodeTag):
                left = compactF(tree.root.leftNode())
                right = compactF(tree.root.rightNode())
                compactTree.root = InternalNode(left, right, compactTree)