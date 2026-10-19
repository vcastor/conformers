#!/bin/sh

AMS_JOBNAME="system_002_conformer_001" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        N         0.7059366317        -0.0346581986         0.1843999962
        N        -0.6978075705        -0.0628275362        -0.2065316617
        H         0.9035458860         0.8157481670         0.7268924984
        H         1.2390897773         0.0696550787        -0.6839606429
        H        -1.0459318777         0.8954545053        -0.3384314134
        H        -1.2096648968        -0.4261998562         0.6030403013
    End
End

Engine ADF
    TotalEnergy Yes
    Basis
        Type TZP
        Core None
    End
    Symmetry nosym
    XC
       GGA PBE
       DISPERSION Grimme3 BJDAMP
    End
    QTAIM
        AnalysisLevel Full
        Spacing 0.1
    End
    ConceptualDFT
        Enabled YES
        AnalysisLevel Full
    End
    Relativity
        Level None
    End
    NumericalQuality VeryGood
EndEngine

eor
