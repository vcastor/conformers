#!/bin/sh

AMS_JOBNAME="system_002_conformer_001" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        C        -1.0994963102        -0.4031402106         0.0016569981
        C        -0.7370284932         0.9254025901         0.0576828466
        N         0.6420369334         0.9255879991         0.0311666672
        C         1.0605757208        -0.3696885424        -0.0376341587
        N         0.0279692716        -1.2094159858        -0.0567991447
        H        -2.1027122722        -0.8219277065         0.0014132820
        H        -1.3137466924         1.8426750889         0.1103656490
        H         1.2402040029         1.7476540030         0.0563302641
        H         2.1117076878        -0.6423346898        -0.0705557172
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
