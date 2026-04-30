#!/bin/sh

AMS_JOBNAME="system_003_conformer_001" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        N         0.7061409587        -0.0348648413         0.1844042499
        N        -0.6979772104        -0.0630416818        -0.2066315544
        H         0.9022681761         0.8153153088         0.7278727116
        H         1.2388067595         0.0728093801        -0.6839374654
        H        -1.0446411727         0.8956824119        -0.3394717873
        H        -1.2098768860        -0.4233019489         0.6044062808
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
