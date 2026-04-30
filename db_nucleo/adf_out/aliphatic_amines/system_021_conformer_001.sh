#!/bin/sh

AMS_JOBNAME="system_021_conformer_001" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        C         1.8869655142        -0.0003059144        -0.3817672820
        C         0.7327554721        -0.2629880194        -0.1107589952
        C        -0.6736957463        -0.5320800380         0.2154593515
        N        -1.5562796459         0.6530630679         0.2191428035
        H         2.9088750118         0.2300185093        -0.6212712845
        H        -0.7253037472        -1.0102683301         1.2057140822
        H        -1.0744443632        -1.2637033632        -0.5027447667
        H        -1.4983332139         1.1041826139        -0.7000975173
        H        -1.1726849856         1.3421219984         0.8745946893
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
