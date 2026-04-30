#!/bin/sh

AMS_JOBNAME="system_009_conformer_002" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        C         1.3568044843        -0.2638538148        -0.2038628246
        C         0.0285719045         0.4618597073        -0.0238397890
        N        -1.1037289550        -0.4836191344        -0.1477719157
        H         1.3954065247        -0.7743251792        -1.1782295755
        H         1.4986001491        -1.0209858569         0.5837374740
        H         2.1978608776         0.4423577032        -0.1467302490
        H         0.0322353052         0.9970722026         0.9449272139
        H        -0.0882207749         1.2256016271        -0.8086133324
        H        -1.0506615600        -1.1540862512         0.6280444900
        H        -1.9788492381         0.0262140900         0.0134316695
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
