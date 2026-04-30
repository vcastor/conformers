#!/bin/sh

AMS_JOBNAME="system_029_conformer_010" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        C        -2.2216544320         0.5619981695        -0.3937870215
        C        -1.2829870587        -0.6379996767        -0.2636487795
        C         0.1437119231        -0.3823438472        -0.7690932524
        N         0.9093757154        -1.6480237039        -0.6955072111
        C         0.8327655526         0.7787361263        -0.0511117775
        O         0.8930419210         0.4819021241         1.3628647823
        H        -2.2633271347         0.9234901456        -1.4329671306
        H        -1.9020686220         1.4009318010         0.2411983578
        H        -3.2432123143         0.2909253245        -0.0925848861
        H        -1.6843388840        -1.4911926640        -0.8322880794
        H        -1.2302317111        -0.9591080036         0.7896400405
        H         0.0879888500        -0.0950623218        -1.8335597506
        H         1.8596239807        -1.4761963241        -1.0434092073
        H         1.0360753844        -1.8765141013         0.2976383113
        H         0.2809197582         1.7190554398        -0.2230754108
        H         1.8514838391         0.9027384768        -0.4582272541
        H         1.4120535999         1.1938105480         1.7805976724
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
