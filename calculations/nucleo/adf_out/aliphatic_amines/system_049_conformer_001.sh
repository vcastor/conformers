#!/bin/sh

AMS_JOBNAME="system_049_conformer_001" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        N         0.0006067685        -0.0000608239         0.0729948884
        H         0.9310014792        -0.1069632792        -0.3459521457
        H        -0.5625313348        -0.7548738815        -0.3339968356
        H        -0.3769017756         0.8626823677        -0.3343850851
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
