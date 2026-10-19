#!/bin/sh

AMS_JOBNAME="system_001_conformer_001" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        O        -1.1071815294        -0.1817927840         0.0000000000
        N        -0.0101664098         0.3393466907         0.0000000000
        O         1.1160818242        -0.1152919938         0.0000000000
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
