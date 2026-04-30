#!/bin/sh

AMS_JOBNAME="system_037_conformer_002" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        N         1.4668258313         0.6083372789        -0.0604964161
        C         0.3138976561         0.3343155102        -0.9374011654
        C        -0.7620218403        -0.5813738722        -0.3607373778
        O        -1.4432049523        -0.0065962051         0.7796677916
        H         1.1478872442         1.0875964778         0.7879222889
        H         1.8718196758        -0.2792282040         0.2574773689
        H        -0.1437526525         1.2979365396        -1.2102945980
        H         0.6848509680        -0.1236354985        -1.8686985550
        H        -0.3231702654        -1.5567785954        -0.0853589260
        H        -1.5421289110        -0.7580185505        -1.1155301190
        H        -0.8189873401        -0.0304143244         1.5302959390
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
