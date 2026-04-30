#!/bin/sh

AMS_JOBNAME="system_001_conformer_001" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        N        -3.3161974930         0.0767200168        -0.2796813877
        C        -1.9283111026         0.0406431156        -0.1214864518
        C        -1.1898087815         1.2301256563         0.0375226013
        C         0.2016889179         1.2038706914         0.1264681688
        C         0.8719677254        -0.0188749771         0.0572131399
        Cl         2.6353531290        -0.0557401563         0.1715307601
        C         0.1647609490        -1.2125992056        -0.0971714936
        C        -1.2267263634        -1.1799044364        -0.1855047678
        H        -3.7898480043        -0.7842504334        -0.0088322534
        H        -3.7647287764         0.8845401050         0.1509486437
        H        -1.7133215518         2.1876775096         0.0918581637
        H         0.7608498178         2.1320679938         0.2515110719
        H         0.6950746466        -2.1645753855        -0.1458089893
        H        -1.7791574954        -2.1149156417        -0.3060673339
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
