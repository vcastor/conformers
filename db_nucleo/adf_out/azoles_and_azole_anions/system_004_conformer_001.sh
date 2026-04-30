#!/bin/sh

AMS_JOBNAME="system_004_conformer_001" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        C        -2.0778810571        -0.4659688378        -0.1260197213
        N        -0.6522552801        -0.1609431696        -0.0408463696
        C         0.3818838336        -1.0770433451        -0.0080930427
        C         1.5392296283        -0.3326140573         0.0780948531
        N         1.2402952670         1.0199850790         0.0949999146
        C        -0.0887644510         1.0806407352         0.0222888022
        H        -2.6374883941         0.4750600984        -0.1334553134
        H        -2.2918609638        -1.0198574534        -1.0487501306
        H        -2.3895710300        -1.0643360699         0.7391688687
        H         0.2004078443        -2.1466759847        -0.0472034765
        H         2.5635336927        -0.6944391176         0.1277779303
        H        -0.6907608422         1.9856973838         0.0118462860
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
