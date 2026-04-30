#!/bin/sh

AMS_JOBNAME="system_001_conformer_001" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        N        -0.7095564324         0.2131855388        -0.1068759841
        O         0.6799172918        -0.2106036014         0.1144199308
        H        -0.6239223101         1.2295901459        -0.2375747564
        H        -0.9157385002        -0.1464020425        -1.0481606532
        H         0.6074813983        -0.7027505983         0.9547225291
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
