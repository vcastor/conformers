#!/bin/sh

AMS_JOBNAME="system_026_conformer_010" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        N         2.2682566477         0.5941219004        -0.6097383675
        C         1.0790542175        -0.1316364689        -0.1151104924
        C        -0.2004697108         0.6182398353        -0.4824183594
        C        -1.4730981361        -0.0797170176        -0.0071537859
        N        -1.5766132092        -0.0760192292         1.4700490000
        H         3.1064901702         0.0518079763        -0.3761929929
        H         2.2405044252         0.5972113952        -1.6358471850
        H         1.1742228518        -0.2083928798         0.9799807864
        H         1.0122067676        -1.1659890083        -0.5061945930
        H        -0.2483971814         0.7198082682        -1.5802636390
        H        -0.1601636573         1.6375230493        -0.0630620990
        H        -1.5080881631        -1.1014310633        -0.4339237411
        H        -2.3470604514         0.4603403986        -0.4004704865
        H        -0.8632110553        -0.7039093007         1.8554338641
        H        -2.4659398310        -0.5116505412         1.7348650720
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
