#!/bin/sh

AMS_JOBNAME="system_020_conformer_008" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        N         1.8891009516        -0.1130470839        -0.0393167468
        C         0.4954284926        -0.4938896472        -0.3466818978
        C        -0.4593617621         0.6303239442         0.0402111053
        N        -1.8478472087         0.2696093226        -0.3114580509
        H         1.9957770659        -0.0576619607         0.9797707392
        H         2.5079075164        -0.8794129424        -0.3217367671
        H         0.4158030177        -0.6768101802        -1.4294456852
        H         0.1776295075        -1.4246067429         0.1640506861
        H        -0.3293607796         0.8547861547         1.1176177193
        H        -0.1856590002         1.5412429278        -0.5142771384
        H        -2.1453157547        -0.5087835429         0.2874429462
        H        -2.4640033481         1.0457283365        -0.0508311027
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
