#!/bin/sh

AMS_JOBNAME="system_024_conformer_008" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        O        -2.7525057341        -0.4239956874         1.0622001186
        C        -2.4940889470         0.7199282865         0.2118864232
        C        -1.2305214337         0.5556405262        -0.6165134555
        N        -0.0561742512         0.3909775549         0.2484705785
        C         1.1798885739         0.1737809242        -0.5115008392
        C         2.3521007746        -0.0139662955         0.4480731490
        O         3.6172290917        -0.1058215668        -0.2403439093
        H        -2.9414800116        -1.1791485187         0.4706591045
        H        -3.3523951196         0.9110169199        -0.4535252982
        H        -2.3860763757         1.5729681129         0.8975292317
        H        -1.3584507355        -0.2935932845        -1.3239413336
        H        -1.0995143705         1.4640021996        -1.2285539845
        H        -0.2294856429        -0.4368653815         0.8306557032
        H         1.1166660378        -0.7011228055        -1.1950831214
        H         1.3647730799         1.0614069176        -1.1388213724
        H         2.4316595750         0.8566108085         1.1138370491
        H         2.1881933909        -0.9087882909         1.0760302986
        H         3.5894542264        -0.9178623332        -0.7832589679
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
