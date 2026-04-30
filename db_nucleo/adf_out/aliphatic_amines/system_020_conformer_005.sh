#!/bin/sh

AMS_JOBNAME="system_020_conformer_005" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        N         0.0352549660        -1.9312761865        -0.3481048170
        C         0.5534600652        -0.5520025898        -0.3868353091
        C        -0.4155933302         0.5189492030         0.1199329306
        N         0.1959547195         1.8599516015         0.0124523832
        H        -0.8318112517        -1.9716384919        -0.8957584343
        H        -0.2534443547        -2.1483714935         0.6126081489
        H         0.8412410634        -0.3150897858        -1.4233300983
        H         1.4769339131        -0.5167818724         0.2152048040
        H        -0.7248454002         0.2605110359         1.1520610136
        H        -1.3251187080         0.5063442984        -0.5024114855
        H         0.9750839346         1.9176402809         0.6778154558
        H        -0.4770169189         2.5592425859         0.3417112151
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
