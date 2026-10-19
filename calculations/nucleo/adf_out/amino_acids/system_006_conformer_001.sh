#!/bin/sh

AMS_JOBNAME="system_006_conformer_001" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        N         0.2028690307        -1.7835253084        -0.0896069242
        C         0.5635536011        -0.5422540457        -0.5489607591
        C         1.5626449003         0.1956318809         0.3393498813
        O         1.1937840030         0.1334488120         1.7170054469
        C        -0.9346322798         0.5169711388        -0.5530410633
        O        -1.1418461906         1.0010351409         0.5678354545
        O        -1.4453532763         0.5097507736        -1.6707275447
        H         0.0852242203        -1.9062239998         0.9162389247
        H        -0.3187941799        -2.4163926651        -0.6905092552
        H         0.8104868136        -0.5324925129        -1.6150229602
        H         2.5360018412        -0.3095245893         0.2390606516
        H         1.6701197311         1.2325514416        -0.0139619195
        H         0.3170925576         0.5875804474         1.7490999225
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
