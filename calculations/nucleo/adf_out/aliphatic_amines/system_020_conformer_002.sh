#!/bin/sh

AMS_JOBNAME="system_020_conformer_002" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        N         1.9015353768        -0.3125142321         0.1059766566
        C         0.4849289453        -0.5503836864        -0.2302847562
        C        -0.4765698983         0.5816305531         0.1594868288
        N        -1.8931850806         0.3437566692        -0.1767262737
        H         2.2022363408         0.5617620668        -0.3399893113
        H         1.9736846533        -0.1283429773         1.1132087039
        H         0.1643918743        -1.4821996852         0.2644731814
        H         0.4129212272        -0.7267643881        -1.3164224532
        H        -0.1560622691         1.5134319216        -0.3353140653
        H        -0.4045300820         0.7580425896         1.2456181527
        H        -2.1938840022        -0.5305040539         0.2692706514
        H        -1.9653683873         0.1595638083        -1.1839515081
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
