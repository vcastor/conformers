#!/bin/sh

AMS_JOBNAME="system_008_conformer_001" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        C        -0.7446065000         0.0288128431        -0.0346274741
        N         0.7319468233        -0.0357255555        -0.0299371614
        H        -1.2006182020         0.1671993819         0.9622476710
        H        -1.0701373058         0.8608870788        -0.6751868596
        H        -1.1470363251        -0.8987470678        -0.4665936838
        H         1.0240761645        -0.7920705971         0.5974115341
        H         1.0949810374         0.8158522621         0.4107311014
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
