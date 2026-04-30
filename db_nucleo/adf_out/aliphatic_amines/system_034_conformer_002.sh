#!/bin/sh

AMS_JOBNAME="system_034_conformer_002" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        N        -2.0148858833        -0.1323963545        -0.2144158690
        C        -0.7590964365        -0.8713851998        -0.0684146165
        C         0.4276208318         0.0762429682        -0.0009824602
        F         0.5532549160         0.8638869517        -1.1191023215
        F         0.3496410557         0.9350930315         1.0749026665
        F         1.6053604730        -0.6222179804         0.1317389490
        H        -2.7182684398        -0.7638003115        -0.6052241307
        H        -2.3677826454         0.1319882229         0.7093878718
        H        -0.6972787008        -1.5148932550         0.8257025887
        H        -0.5986582781        -1.5073996114        -0.9485271999
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
