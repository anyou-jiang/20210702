import copy
import numpy as np
from NodeTag import NodeTag


class NormPolishExpression:

    @staticmethod
    def _isViolatingBallotingIfSwap(expression, indexOfOperator):  # indexOfOperator must be pointed to an operator
        assert (NodeTag.isOperator(expression[indexOfOperator]))
        p = indexOfOperator
        Np = sum([NodeTag.isOperator(expression[i]) for i in range(0, indexOfOperator)]) + 1
        if 2 * Np < p:
            return False
        else:
            return True

    def __init__(self, expression):  # must be a list?
        self._expression = expression

    def numOfTask(self):
        return sum([NodeTag.isOperand(x) for x in self._expression])

    def getExpressionInfoCompactFormat(self):
        return ''.join(["{}-".format(self._expression[i]) for i in range(len(self._expression) - 1)]) + "{}".format(self._expression[-1])

    def isValid(self):
        return self._checkBallotingProperty()

    def __iter__(self):
        return iter(self._expression)

    def isFullUnqiueExpression(self):
        # unique form like, 0, 1, F, 2, F, 3, F, 4, F, 5, F
        if len(self._expression) <= 2:
            return False
        uniqueLabel = self._expression[2]
        for index in range(2, len(self._expression), 2):
            if not NodeTag.isSameTag(uniqueLabel, self._expression[index]):
                return False
        for index in range(1, len(self._expression), 2):
            if not NodeTag.isOperand(self._expression[index]):
                return False
        return True

    def randomlySwapTwoAdjacentOperands(self):
        newExpression = copy.deepcopy(self._expression)
        leafIndices = [index for index in range(len(newExpression))
                       if NodeTag.isOperand(newExpression[index])]
        randomInt = np.random.randint(0, len(leafIndices))
        swapIndex_i = leafIndices[randomInt]
        swapIndex_ip1 = leafIndices[(randomInt + 1) % len(leafIndices)]
        newExpression[swapIndex_i], newExpression[swapIndex_ip1] = newExpression[swapIndex_ip1], newExpression[
            swapIndex_i]
        return NormPolishExpression(newExpression)

    def randomlyInvertChain(self):
        newExpression = copy.deepcopy(self._expression)
        chainStartIndices = [index for index in range(len(newExpression))
                             if
                             NodeTag.isOperator(newExpression[index]) and NodeTag.isOperand(newExpression[index - 1])]
        randomInt = np.random.randint(0, len(chainStartIndices))
        chainStartIndex = chainStartIndices[randomInt]
        while chainStartIndex < len(newExpression):
            if NodeTag.isOperand(newExpression[chainStartIndex]):
                break
            newExpression[chainStartIndex] = NodeTag.invertTag(newExpression[chainStartIndex])
            chainStartIndex = chainStartIndex + 1
        return NormPolishExpression(newExpression)

    def testSwapTwoAdjacentOperandOperator(self):
        newExpression = copy.deepcopy(self._expression)
        indicesOfOperandFollowedByOperator = [index for index in range(len(newExpression) - 1)
                                              if NodeTag.isOperand(newExpression[index])
                                              and NodeTag.isOperator(newExpression[index + 1])]
        indexOfOperand = indicesOfOperandFollowedByOperator[
            np.random.randint(0, len(indicesOfOperandFollowedByOperator))]
        indexOfOperator = indexOfOperand + 1
        if not NodeTag.isSameTag(newExpression[indexOfOperand - 1], newExpression[indexOfOperand + 1]):
            violated = NormPolishExpression._isViolatingBallotingIfSwap(newExpression, indexOfOperator)
            if not violated:
                newExpression[indexOfOperand], newExpression[indexOfOperator] = \
                    newExpression[indexOfOperator], newExpression[indexOfOperand]
                return True, NormPolishExpression(newExpression)
        return False, None

    def testSwapTwoAdjacentOperatorAndOperand(self):
        newExpression = copy.deepcopy(self._expression)
        indicesOfOperatorFollowedByOperand = [index for index in range(len(newExpression) - 1)
                                              if NodeTag.isOperator(newExpression[index])
                                              and NodeTag.isOperand(newExpression[index + 1])]
        indexOfOperator = indicesOfOperatorFollowedByOperand[np.random.randint(0, len(indicesOfOperatorFollowedByOperand))]
        indexOfOperand = indexOfOperator + 1
        if not NodeTag.isSameTag(newExpression[indexOfOperator], newExpression[indexOfOperator + 2]):
            newExpression[indexOfOperator], newExpression[indexOfOperand] = \
                newExpression[indexOfOperand], newExpression[indexOfOperator]
            return True, NormPolishExpression(newExpression)
        return False, None

