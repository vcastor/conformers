#!/bin/sh

AMS_JOBNAME="system_032_conformer_001" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        O        -2.6772373273        -0.1929023018        -1.1198326681
        C        -2.2050712238         0.5046881715         0.0590514761
        C        -0.7374752630         0.8152741694        -0.1457672829
        N         0.0548526433        -0.4217282889        -0.2219924024
        C         1.4328346146        -0.2120982053        -0.6949293804
        C         2.2958898892         0.2473052040         0.4811149193
        O         2.0569171289        -0.6173263638         1.6113839114
        H        -3.5791713993        -0.5084621329        -0.9241321083
        H        -2.3416149415        -0.1276854644         0.9527907185
        H        -2.7635771910         1.4448663261         0.2014474897
        H        -0.6223752320         1.4296854028        -1.0630679588
        H        -0.3903665366         1.4265410659         0.7016903492
        H        -0.4222241864        -1.0609953130        -0.8625559982
        H         1.4994787537         0.5246882525        -1.5197401974
        H         1.8090758472        -1.1770036698        -1.0652212852
        H         3.3619590297         0.1964697456         0.2197871512
        H         2.0587608330         1.2927905125         0.7519220186
        H         1.1062880283        -0.8675693363         1.4705871869
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
