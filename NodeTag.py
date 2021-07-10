
class NodeTag:

    def __init__(self, tag):
        self._tag = tag

    @staticmethod
    def isOperator(tag):
        return tag == 'F' or tag == 'T'

    @staticmethod
    def isOperand(tag):
        return tag != 'F' and tag != 'T'

    @staticmethod
    def isF(tag):
        return tag == 'F'
    
    @staticmethod
    def isT(tag):
        return tag == 'T'

    @staticmethod
    def isSameTag(tag1, tag2):
        return tag1 == tag2

    @staticmethod
    def invertTag(tag):
        if tag == "F":
            return "T"
        elif tag == "T":
            return "F"
        else:
            raise(ValueError("{} is not a valid operator.".format(tag)))


