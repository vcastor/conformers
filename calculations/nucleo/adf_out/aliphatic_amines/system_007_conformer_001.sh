#!/bin/sh

AMS_JOBNAME="system_007_conformer_001" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        N         0.0006058694        -0.0000603755         0.0730562046
        H         0.9309016037        -0.1069534834        -0.3462367575
        H        -0.5624662644        -0.7548050085        -0.3342808595
        H        -0.3768544764         0.8625974670        -0.3346684974
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
