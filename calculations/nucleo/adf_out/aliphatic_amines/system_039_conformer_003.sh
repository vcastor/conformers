#!/bin/sh

AMS_JOBNAME="system_039_conformer_003" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        C         1.8899105001         0.3479280294        -0.0633983415
        C         0.6507702261         0.3365678083        -0.5672385293
        C        -0.6023163783         0.2636265683         0.2559204733
        N        -1.4967242061        -0.8052305020        -0.2437698746
        H         2.7681701294         0.4231260871        -0.7080978250
        H         2.0633798648         0.2900572537         1.0155423803
        H         0.5019411844         0.3853999935        -1.6531193639
        H        -0.3344621321         0.1577393854         1.3239011471
        H        -1.1496214253         1.2166730396         0.1533583109
        H        -2.3589329919        -0.7935786153         0.3105948282
        H        -1.0636019837        -1.7127658573        -0.0407342412
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
