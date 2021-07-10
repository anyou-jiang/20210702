import enum


class Parameters:
    class FeatureConstrains(enum.Enum):
        ENoConstrain = 0
        ETaskPrecedence = 1

    class PerturbOperationSelectionRules(enum.Enum):
        Randomly = 0

    class SlicingTreeExpressionKeyTypes(enum.Enum):
        PostOrderFullForChannelAwared = 0
        CompactFForChannelUnAwared = 1

    class UEPriorityWeightingOptions(enum.Enum):
        AllUESamePriorityWeighting = 0
        FixedWeightingGapBetweenEachUE = 1
        ReciprocalOfResourceElementNumber = 2

    reservedNumPrbPerUe = 1.0
    simCount = 1
    numOfPRBNumToSim = 10
    toUseWeightedDelayAsCost = False
    featureConstrain = FeatureConstrains.ETaskPrecedence
    perturbOperationSelectionRule = PerturbOperationSelectionRules.Randomly

    @staticmethod
    def paramsDescriptions():
        return 'simCount = {}\n' \
               'toUseWeightedDelayAsCost = {}\n' \
               'featureConstrain = {}\n' \
               'perturbOperationSelectionRule = {}\n'.format(Parameters.simCount,
                                                             Parameters.toUseWeightedDelayAsCost,
                                                             Parameters.FeatureConstrains(Parameters.featureConstrain),
                                                             Parameters.PerturbOperationSelectionRules(
                                                                 Parameters.perturbOperationSelectionRule))
