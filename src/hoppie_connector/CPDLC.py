from enum import StrEnum

class CpdlcResponseRequirement(StrEnum):
    WILCO_UNABLE    = W_U = 'WU'
    AFFIRM_NEGATIVE = A_N = 'AN'
    ROGER           = R = 'R'
    NOT_REQUIRED    = NE = 'NE'
    NO              = N = 'N'
    YES             = Y = 'Y'

    def __repr__(self) -> str:
        return f"CpdlcResponseRequirement.{self.name}"