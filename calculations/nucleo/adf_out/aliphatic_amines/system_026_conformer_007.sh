#!/bin/sh

AMS_JOBNAME="system_026_conformer_007" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        N         1.4697331407        -1.1231040937        -0.9971423141
        C         1.3938497027         0.0262750192        -0.0706812975
        C         0.1661931629         0.9354250815        -0.2233472601
        C        -1.1785662167         0.2418284613        -0.0031783054
        N        -1.2681012851        -0.3444739856         1.3524224753
        H         0.6546270867        -1.7258749019        -0.8414224869
        H         1.3598431068        -0.7799637371        -1.9585290960
        H         2.3031800489         0.6316111865        -0.2080503231
        H         1.4274299726        -0.3730933745         0.9538531659
        H         0.1652984537         1.3849254411        -1.2310236222
        H         0.2602121610         1.7733752627         0.4909617448
        H        -1.9868846907         0.9670518464        -0.2130422763
        H        -1.3005302637        -0.5781348658        -0.7300318238
        H        -2.2004379340        -0.7535452819         1.4708292453
        H        -1.2281527614         0.4180052562         2.0383351551
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
