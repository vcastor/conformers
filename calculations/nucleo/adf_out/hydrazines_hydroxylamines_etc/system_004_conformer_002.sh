#!/bin/sh

AMS_JOBNAME="system_004_conformer_002" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        C        -1.1156903296        -0.6504062728         0.3632315884
        N         0.0214723534        -0.0048333949        -0.2997089793
        C         1.2434999355        -0.7734336189        -0.0444006658
        N         0.2060866132         1.3025639257         0.3774929489
        H        -2.0271187833        -0.0596091736         0.1916366104
        H        -0.9561084271        -0.7509021764         1.4568924840
        H        -1.2610412571        -1.6467903099        -0.0743761982
        H         2.0992346800        -0.2769933171        -0.5246208834
        H         1.1299102188        -1.7728176511        -0.4845011885
        H         1.4524849150        -0.8734389737         1.0410165834
        H         0.9587067264         1.7600355011        -0.1553636016
        H        -0.6267892709         1.8453825276         0.1104594332
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
