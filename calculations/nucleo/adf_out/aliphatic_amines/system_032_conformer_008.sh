#!/bin/sh

AMS_JOBNAME="system_032_conformer_008" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        O        -2.7465248120        -0.4185879162         1.0663603841
        C        -2.4923784879         0.7201816731         0.2086936057
        C        -1.2307578766         0.5519920201        -0.6222727858
        N        -0.0556531848         0.3932647031         0.2414500626
        C         1.1792917056         0.1667086716        -0.5162046097
        C         2.3515464221        -0.0118721208         0.4452113118
        O         3.6166401430        -0.1123768602        -0.2407801219
        H        -2.9449966276        -1.1758069857         0.4808560261
        H        -3.3532098497         0.9074947953        -0.4546882954
        H        -2.3819452132         1.5771290998         0.8890101979
        H        -1.3605560625        -0.3013207337        -1.3249796961
        H        -1.1014282811         1.4566251877        -1.2403148683
        H        -0.2305992692        -0.4261277337         0.8347660811
        H         1.1158759077        -0.7150817563        -1.1914272810
        H         1.3654144299         1.0474230514        -1.1528430458
        H         2.4310195040         0.8658849164         1.1013954786
        H         2.1861135721        -0.8992254195         1.0836236005
        H         3.5890914473        -0.9297668183        -0.7753201049
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
