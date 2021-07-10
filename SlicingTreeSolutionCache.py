
class SlicingTreeSolutionCache:

    solutionCache = {}
    hitCachedCount = 0

    @staticmethod
    def reset():
        SlicingTreeSolutionCache.solutionCache = {}
        SlicingTreeSolutionCache.hitCachedCount = 0

    @staticmethod
    def cacheSize():
        return len(SlicingTreeSolutionCache.solutionCache)

    @staticmethod
    def addCache(expression, solution):
        SlicingTreeSolutionCache.solutionCache[expression] = solution

    @staticmethod
    def fetchCache(expression):
        defaultValueIfNotExisting = False
        cached = SlicingTreeSolutionCache.solutionCache.get(expression, defaultValueIfNotExisting)
        if cached is defaultValueIfNotExisting:
            return False, None
        else:
            return True, cached


