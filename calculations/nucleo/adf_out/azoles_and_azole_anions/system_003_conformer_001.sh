#!/bin/sh

AMS_JOBNAME="system_003_conformer_001" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        C        -1.0998505331        -0.4030806292         0.0016380705
        C        -0.7368745762         0.9253230760         0.0577057103
        N         0.6420057105         0.9253054242         0.0311530802
        C         1.0608264375        -0.3692859767        -0.0376290382
        N         0.0279379246        -1.2094792814        -0.0567836437
        H        -2.1030863499        -0.8218458656         0.0014374024
        H        -1.3133578143         1.8427216579         0.1103822056
        H         1.2402834506         1.7473649936         0.0562586990
        H         2.1118822378        -0.6419271562        -0.0706593384
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
