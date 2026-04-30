#!/bin/sh

AMS_JOBNAME="system_026_conformer_011" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        N         1.6091708255         0.3255229416        -0.9972068247
        C         1.3301045425        -0.3126176229         0.3106069097
        C         0.1020115899         0.3035035631         0.9834722327
        C        -1.2399278237        -0.1267073750         0.3856059672
        N        -1.3948073784         0.3128341470        -1.0217448934
        H         2.3272695162        -0.2205881854        -1.4847767225
        H         0.7507044248         0.2288390047        -1.5572742794
        H         2.2106413845        -0.1692641130         0.9570678360
        H         1.1712450380        -1.4067384375         0.2260436883
        H         0.0997197362         0.0158346542         2.0469380059
        H         0.1858695097         1.4048396360         0.9552420810
        H        -2.0547595108         0.2436491510         1.0360531683
        H        -1.2990638305        -1.2276632262         0.3956425630
        H        -2.3050389029        -0.0081963678        -1.3668976897
        H        -1.4554454367         1.3370595444        -1.0388190615
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
