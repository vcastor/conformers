#!/bin/sh

AMS_JOBNAME="system_003_conformer_001" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        C        -3.1115245545         0.0940191128         0.9660277017
        O        -2.3654727341        -0.0061421539        -0.2609697256
        C        -0.9858972259        -0.0103628132        -0.1411414178
        C        -0.2600198817        -0.0674858399        -1.3413982179
        C         1.1323860401        -0.0724045489        -1.3260135254
        C         1.8440822682        -0.0209044659        -0.1109604282
        N         3.2530811242         0.0530066596        -0.1035307507
        C         1.1081052890         0.0277914140         1.0827186475
        C        -0.2926764174         0.0343657082         1.0750437547
        H        -2.9228643189        -0.7734962400         1.6173132152
        H        -4.1662871284         0.1117817740         0.6734071211
        H        -2.8612982415         1.0212484625         1.5047989283
        H        -0.8014113560        -0.1075769232        -2.2889519585
        H         1.6810617504        -0.1138666398        -2.2702765149
        H         3.6771620005        -0.4118739436        -0.9074107955
        H         3.6633192799        -0.3211168965         0.7532231097
        H         1.6353332465         0.0629547219         2.0395082483
        H        -0.8244246687         0.0713715124         2.0252915767
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
