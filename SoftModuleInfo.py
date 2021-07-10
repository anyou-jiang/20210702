import sys

class SoftModuleInfo:
    infoMap = []
    ueWeights = {}
    Hmax = 100
    Wmax = 12

    allPossibleShapes = None

    @staticmethod
    def setHmax(H):
        SoftModuleInfo.Hmax = H

    @staticmethod
    def setWmax(W):
        SoftModuleInfo.Wmax = W

    @staticmethod
    def setInfoMap(infoMap):
        SoftModuleInfo.infoMap = infoMap

    @staticmethod
    def setUeWeights(ueWeights):
        SoftModuleInfo.ueWeights = ueWeights

    @staticmethod
    def getModuleInfoByTag(tag):
        return SoftModuleInfo.infoMap[tag]

    @staticmethod
    def getShapeInfoById(id):
        for moduleInfo in SoftModuleInfo.infoMap:
            for shapeInfo in moduleInfo:
                assert(len(shapeInfo["id"]) == 1)
                if shapeInfo["id"][0] == id:
                    return shapeInfo
        return None

    @staticmethod
    def getInfoMapLog():
        log = ''
        for (index, infoItem) in enumerate(SoftModuleInfo.infoMap):
            log = log + "[{}]------------".format(index) + "\n"
            for (shapeIndex, shape) in enumerate(infoItem):
                log = log + ('    [{}] {}'.format(shapeIndex, shape)) + "\n"
        return log

