#!/bin/sh

AMS_JOBNAME="system_033_conformer_004" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        N         1.5674386253         0.0243150822        -0.0917528386
        C         0.3057285446         0.3044329377        -0.8030497990
        C        -0.7995176252        -0.6173827146        -0.3175339495
        O        -1.0756554012        -0.4482901446         1.0948366729
        H         2.2645158603         0.7236837026        -0.3658600466
        H         1.4055566970         0.1926428886         0.9075787420
        H        -0.0322149398         1.3548940639        -0.6969993134
        H         0.4545665151         0.1207733862        -1.8793535729
        H        -1.7139586733        -0.4512704463        -0.9109225146
        H        -0.4946678158        -1.6678106618        -0.4281698274
        H        -1.4311737448         0.4549082089         1.2075732736
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
