#!/bin/sh

AMS_JOBNAME="system_001_conformer_002" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        N        -0.7647873949         0.0217574456         0.2798624030
        O         0.6526908089        -0.3237885755         0.3408050124
        H        -0.7970615853         1.0415134782         0.1446183025
        H        -1.1099827953        -0.3760231460        -0.6044868685
        H         1.0573224141         0.0195602402        -0.4842677831
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
