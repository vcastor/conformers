#!/bin/sh

AMS_JOBNAME="system_007_conformer_002" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        N        -0.7645087561         0.0218666701         0.2795379555
        O         0.6525966615        -0.3236138410         0.3405127103
        H        -0.7976579806         1.0417283061         0.1452909313
        H        -1.1106819226        -0.3763137434        -0.6042476114
        H         1.0579443736         0.0193315881        -0.4843186670
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
