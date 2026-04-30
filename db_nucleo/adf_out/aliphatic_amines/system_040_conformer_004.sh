#!/bin/sh

AMS_JOBNAME="system_040_conformer_004" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        C         1.6878170469         0.3520904481        -0.3680205136
        C         0.3944648868        -0.2533478431        -0.9218625790
        C        -0.8392701808         0.0701303381        -0.0788660527
        N        -0.7665681912        -0.5640518580         1.2563474205
        H         2.5417852738         0.1376436051        -1.0271560269
        H         1.9364436001        -0.0513488479         0.6259797264
        H         1.6006189001         1.4466206254        -0.2750214923
        H         0.4962251553        -1.3492611241        -0.9997252529
        H         0.2205599304         0.1240837835        -1.9426471592
        H        -0.9546255601         1.1714026672        -0.0213509129
        H        -1.7375882651        -0.3193700522        -0.5820035317
        H        -1.6171147777        -0.3273567694         1.7775705861
        H        -0.0116580621        -0.1212405746         1.7913482287
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
