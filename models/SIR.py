import jax.numpy as np

def SIR(N, Ii, Ri, beta, gamma, days):
    """
    Integrate the SIR model for a set number of days.

    Parameters:
    -----------
    N: float
        Populaiton of the region.
    Ii: float
        Starting number of infected individuals.
    Ri: float
        Starting number of removed individuals.
    beta: float
        Transmitivity of the virus. New infections per person per day.
    gamma: float
        Inverse of time to removal of an individual.
    """
    Si = N - Ii - Ri
    SIR = [np.array([Si, Ii, Ri])]

    for i in range(1, days):

        S, I = SIR[i-1][0], SIR[i-1][1]
        dS = -beta*S*I/N
        dR = gamma*I
        SIR.append(SIR[i-1] + np.array([dS, -dS-dR, dR]))

    return np.array(SIR)

def SIRD(N, Ii, Ri, Di, beta, gammaR, gammaD, days):
    """
    Integrate the SIR model for a set number of days.

    Parameters:
    -----------
    N: float
        Populaiton of the region.
    Ii: float
        Starting number of infected individuals.
    Ri: float
        Starting number of recovered individuals.
    Di: float
        Starting number of dead individuals.
    beta: float
        Transmitivity of the virus. New infections per person per day.
    gammaR: float
        Inverse of time to recovery of an individual.
    gammaD: float
        Inverse of time to death of an individual.
    """

    Si = N - Ii - Ri - Di
    SIRD = [np.array([Si, Ii, Ri, Di])]

    for i in range(1, days):

        S, I = SIRD[i-1][0], SIRD[i-1][1]
        dS = -beta*S*I/N
        dR = gammaR*I
        dD = gammaD*I
        SIRD.append(SIRD[i-1] + np.array([dS, -dS-dR-dD, dR, dD]))

    return np.array(SIRD)
