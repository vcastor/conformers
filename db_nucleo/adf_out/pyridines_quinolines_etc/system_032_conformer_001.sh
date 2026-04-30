#!/bin/sh

AMS_JOBNAME="system_032_conformer_001" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        C        -0.2063374326         1.3998305436         0.0643234632
        C        -1.2896899932         0.5195032832         0.0221653547
        C        -1.0354519033        -0.8529408727        -0.0397606737
        N         0.2040032961        -1.3836295385        -0.0625711743
        C         1.2377351506        -0.5189091366        -0.0225563130
        C         1.0849880897         0.8686239213         0.0398658317
        H        -0.3655078137         2.4787778904         0.1142863790
        H        -2.3179646817         0.8849396255         0.0380361881
        H        -1.8661150513        -1.5642079898        -0.0734348689
        H         2.2382758238        -0.9611357241        -0.0423515371
        H         1.9639261724         1.5148353843         0.0699087084
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
