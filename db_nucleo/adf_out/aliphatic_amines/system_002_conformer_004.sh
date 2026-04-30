#!/bin/sh

AMS_JOBNAME="system_002_conformer_004" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        C         1.6881110986         0.3519911039        -0.3682514156
        C         0.3946881725        -0.2534460618        -0.9220373395
        C        -0.8390130263         0.0699075724        -0.0789101607
        N        -0.7661009381        -0.5642014833         1.2567257972
        H         2.5421767484         0.1365650746        -1.0269821174
        H         1.9359815316        -0.0505171497         0.6263238479
        H         1.6010633375         1.4466236948        -0.2763406102
        H         0.4965961139        -1.3494031760        -1.0002821663
        H         0.2205691306         0.1240695933        -1.9427460142
        H        -0.9543904308         1.1710097745        -0.0207497753
        H        -1.7373901371        -0.3196100688        -0.5818750749
        H        -1.6173413986        -0.3278626635         1.7770940796
        H        -0.0124754261        -0.1193172475         1.7919670333
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
