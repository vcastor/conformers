#!/bin/sh

AMS_JOBNAME="system_045_conformer_002" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        C         1.2878360306         0.8255447197        -0.1131502710
        C        -0.0316456663         1.4769846333         0.3241175927
        C        -1.2256536820         0.6581693507        -0.1687958549
        N        -1.1281642749        -0.7250194222         0.3342939137
        C         0.0833515251        -1.3864964602        -0.1868220707
        C         1.3308361926        -0.6507614113         0.3054023166
        H         2.1476189495         1.3725579009         0.3037188534
        H         1.3714838179         0.8884174761        -1.2129312570
        H        -0.1049018982         2.5051465533        -0.0631178668
        H        -0.0694518325         1.5353514402         1.4253486029
        H        -1.2438240615         0.6862383180        -1.2807941814
        H        -2.1706976336         1.0944336296         0.1881310614
        H        -1.9462889015        -1.2457448523         0.0054406220
        H         0.0863805696        -2.4315343718         0.1576523422
        H         0.0922908258        -1.4015959789        -1.2990323966
        H         1.3761061029        -0.7232458190         1.4055757976
        H         2.2312280299        -1.1426908686        -0.0941767289
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
