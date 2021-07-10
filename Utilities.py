from SoftModuleInfo import SoftModuleInfo

def overrides(interface_class):
    def overrider(method):
        assert (method.__name__ in dir(interface_class))
        return method

    return overrider


def LOG(info, level=0):
    if level > 0:
        print(info)


def getSumQueueingDelay(solution):
    bestShapes = solution["bestShapes"]
    startPositions = bestShapes["s"]
    shapeIds = bestShapes["id"]
    sumOfDelay = 0
    for (startPos, shapeId) in zip(startPositions, shapeIds):
        shapeInfo = SoftModuleInfo.getShapeInfoById(shapeId)
        width = shapeInfo["w"]
        sumOfDelay += (startPos + width)
    return sumOfDelay

def is235Exponential(num):
    while num > 0:
        if num % 2 == 0:
            num = num / 2
            continue
        if num % 3 == 0:
            num = num / 3
            continue
        if num % 5 == 0:
            num = num / 5
            continue
        break
    if num == 1:
        return True
    else:
        return False
