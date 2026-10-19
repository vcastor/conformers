#!/bin/sh

AMS_JOBNAME="system_010_conformer_002" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        C         1.3875098500         0.1119061609         0.0017370771
        C        -0.0655747832         0.0019829918         0.4783925293
        C        -0.9016946722         1.1841027126        -0.0087753285
        N        -0.7275161943        -1.2596102876         0.0633618566
        H         1.4293573415         0.1272728563        -1.0997837794
        H         1.9831399930        -0.7433407090         0.3547822071
        H         1.8600995894         1.0342746956         0.3741213637
        H        -0.0689825579         0.0038962638         1.5820238985
        H        -0.9285040712         1.2050802500        -1.1110207852
        H        -1.9354242901         1.1133286986         0.3582308345
        H        -0.4719208854         2.1355927716         0.3352970418
        H        -0.7231901747        -1.2957107475        -0.9643866587
        H        -0.1330064343        -2.0469747465         0.3473831414
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
