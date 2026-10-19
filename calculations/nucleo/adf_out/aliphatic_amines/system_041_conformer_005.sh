#!/bin/sh

AMS_JOBNAME="system_041_conformer_005" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        C         2.5115653778         0.2700246792         0.2287550559
        C         1.1057252761        -0.3347791716         0.2461564419
        C         0.0081732347         0.7186185055         0.0606430764
        C        -1.4117596615         0.1565398012         0.1214111160
        N        -1.6966346118        -0.7299702252        -1.0293997462
        H         2.6278256315         1.0181834230         1.0291314263
        H         3.2850076405        -0.4991620884         0.3715617054
        H         2.7115442695         0.7744916286        -0.7298790524
        H         0.9392371730        -0.8619828173         1.2022499514
        H         1.0329884995        -1.0984184697        -0.5469970284
        H         0.1118196057         1.4853997476         0.8474892572
        H         0.1496797213         1.2333163932        -0.9064808957
        H        -1.5552399310        -0.3509059452         1.0967284181
        H        -2.1335404141         0.9871439387         0.0850084190
        H        -2.6639937554        -1.0612263966        -0.9544056015
        H        -1.1303575011        -1.5804785098        -0.9402387118
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
