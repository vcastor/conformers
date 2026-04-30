#!/bin/sh

AMS_JOBNAME="system_002_conformer_001" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        N        -1.2739143513        -0.0043145243         0.0000000000
        C        -0.0457867493        -0.0001383638         0.0000000000
        O         1.1496339589         0.0038810660         0.0000000000
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
