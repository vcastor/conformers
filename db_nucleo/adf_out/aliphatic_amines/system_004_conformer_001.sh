#!/bin/sh

AMS_JOBNAME="system_004_conformer_001" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        C         1.8956505766         0.4933599113        -0.2023453348
        C         0.5836823947        -0.2508597530        -0.4638567498
        C        -0.5544188239         0.2372019562         0.4387678039
        N        -1.8581358857        -0.4305389810         0.2518656937
        H         2.2222402394         0.3618690582         0.8410878943
        H         1.7792303439         1.5735850558        -0.3819537591
        H         2.7033002854         0.1303461417        -0.8541689046
        H         0.2831545045        -0.1247233219        -1.5183359249
        H         0.7267359904        -1.3335674735        -0.3045289234
        H        -0.7039432793         1.3186292700         0.2826086574
        H        -0.2603081332         0.1128700664         1.4943433649
        H        -1.7290187076        -1.4405136465         0.3820710825
        H        -2.1371507108        -0.3316399451        -0.7310427509
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
