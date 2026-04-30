#!/bin/sh

AMS_JOBNAME="system_033_conformer_007" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        N         1.6589600740        -0.1003259902         0.1093646480
        C         0.4031932986         0.3308621840        -0.5345658798
        C        -0.7319325938        -0.6009492476        -0.1206151825
        O        -1.9749711923        -0.2806173389        -0.7802316966
        H         2.4249001004         0.4858833635        -0.2356638912
        H         1.6053794206         0.1049186006         1.1130111022
        H         0.5332077179         0.2724471457        -1.6257472836
        H         0.1189472031         1.3743325510        -0.2923290828
        H        -0.4921063745        -1.6338209785        -0.4093507473
        H        -0.8605289411        -0.5754019733         0.9769272524
        H        -2.2344306706         0.6135679866        -0.4844524122
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
