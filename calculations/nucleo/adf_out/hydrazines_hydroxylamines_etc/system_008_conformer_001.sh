#!/bin/sh

AMS_JOBNAME="system_008_conformer_001" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        C        -1.1933120380         0.3192585545         0.2021007130
        N         0.1112843225        -0.2667698471         0.5202081046
        O         0.9794881060        -0.0421932333        -0.6496860432
        H        -1.1248588534         1.4143988970         0.2438139137
        H        -1.5742725077         0.0138875976        -0.7876949000
        H        -1.8986071841        -0.0204757796         0.9747259860
        H        -0.0023888523        -1.2876918552         0.5025813698
        H         1.7254957074         0.4524965241        -0.2580566541
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
