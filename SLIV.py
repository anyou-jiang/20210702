
class SLIV:

    allowedSLIVs = None

    @staticmethod
    def isAllowedSLIV(S, L):
        if SLIV.allowedSLIVs is None:
            return True

        for sliv in SLIV.allowedSLIVs:
            if sliv == (S, L):
                return True
        return False
