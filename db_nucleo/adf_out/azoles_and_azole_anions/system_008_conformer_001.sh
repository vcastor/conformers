#!/bin/sh

AMS_JOBNAME="system_008_conformer_001" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        C        -2.1505499209        -0.1376652134         0.0645835317
        C        -0.6609537994        -0.0915240424         0.0259404771
        N         0.1691403649        -1.1308655526         0.1459694353
        C         1.4514825604        -0.6044469881         0.0495745643
        C         1.3956875111         0.7586247625        -0.1288628027
        N         0.0492356513         1.0644020538        -0.1436985256
        H        -2.4764770162        -1.1737786844         0.2108438381
        H        -2.5479413365         0.4747338513         0.8877448370
        H        -2.5862589486         0.2382574262        -0.8733174899
        H         2.3351520402        -1.2344868336         0.1144128820
        H         2.1616347189         1.5181302071        -0.2453810668
        H        -0.3456368095         1.9945185407        -0.2597394530
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
