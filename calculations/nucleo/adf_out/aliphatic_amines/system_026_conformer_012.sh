#!/bin/sh

AMS_JOBNAME="system_026_conformer_012" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        N         1.5678430254        -0.2026435008         1.3331668859
        C         1.3975160619        -0.4094344162        -0.1234357551
        C         0.1656890743         0.3222172233        -0.6542127108
        C        -1.1511782184        -0.1710489294        -0.0628945871
        N        -2.2969882118         0.5367136351        -0.6819615174
        H         2.4425566968        -0.6508308880         1.6251748413
        H         1.7236251839         0.7985477486         1.4980925843
        H         2.2805226765        -0.0837901794        -0.7038470050
        H         1.2832857390        -1.4921788419        -0.2965432708
        H         0.2734579309         1.4039987466        -0.4516701237
        H         0.1328383546         0.2119113233        -1.7503286471
        H        -1.2637541375        -1.2469008362        -0.2759881988
        H        -1.1234511074        -0.0602474944         1.0351199920
        H        -3.1601436864         0.2142744519        -0.2318180315
        H        -2.2341256972         1.5297192719        -0.4289014754
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
