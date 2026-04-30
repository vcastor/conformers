#!/bin/sh

AMS_JOBNAME="system_029_conformer_011" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        C        -2.4816388749        -0.0585764404        -0.5498914487
        C        -1.1849413068        -0.0163238513         0.2576223345
        C         0.0801653880         0.0175187403        -0.6047694307
        N         0.2227355182        -1.2508616540        -1.3478043710
        C         1.3220814129         0.3243185135         0.2347142110
        O         1.2104821149         1.6639302064         0.7708805067
        H        -2.5064541330        -0.9354213436        -1.2118154156
        H        -3.3588173281        -0.1034495312         0.1115167288
        H        -2.5792543299         0.8405788774        -1.1780744109
        H        -1.1214157862        -0.8955078302         0.9246565781
        H        -1.1777947375         0.8692399199         0.9109936680
        H        -0.0219509499         0.8251208670        -1.3516424191
        H         1.1004798526        -1.2310734824        -1.8787291613
        H         0.3368414937        -2.0143290970        -0.6700011160
        H         1.4079496320        -0.4140346994         1.0539354484
        H         2.2228305642         0.2425832524        -0.3986856259
        H         2.0079218375         1.8234350656         1.3097733272
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
