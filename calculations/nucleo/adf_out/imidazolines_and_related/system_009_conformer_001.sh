#!/bin/sh

AMS_JOBNAME="system_009_conformer_001" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        C         2.3860110003        -0.0879456145        -0.4671928260
        C         0.9224689304        -0.1271169605        -0.1063728958
        N         0.2733375533        -1.2550306907        -0.1588419772
        C        -1.1583314628        -1.1904362708         0.1776967488
        C        -1.8040878946         0.1430323238        -0.2074897649
        C        -1.0464737120         1.2779711709         0.4730965033
        N         0.3955224002         1.0773277407         0.2880651192
        H         2.5533115286         0.5721028859        -1.3324672343
        H         2.7310065267        -1.0971649224        -0.7155517435
        H         2.9839113094         0.3033997625         0.3694753913
        H        -1.6666495492        -2.0234419861        -0.3316420528
        H        -1.2887730051        -1.3632381743         1.2627059150
        H        -1.7548089456         0.2671903515        -1.3011815340
        H        -2.8627638976         0.1670586617         0.0869180120
        H        -1.2854468756         1.3014474153         1.5496853846
        H        -1.3215781263         2.2548680443         0.0521912990
        H         0.9631224147         1.9023852251         0.1163284265
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
