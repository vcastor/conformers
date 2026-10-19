#!/bin/sh

AMS_JOBNAME="system_007_conformer_001" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        C        -2.1509216282        -1.5265292254        -0.4654566389
        N        -1.6102670143        -0.2053399481        -0.1616353338
        C        -2.5228900582         0.8672603484         0.2230277180
        C        -0.2623892555        -0.0297462820        -0.0411263036
        C         0.3063336212         1.2142919218         0.3452817392
        C         1.6863631484         1.3413193326         0.4268560912
        N         2.5753991621         0.3523485316         0.1741747542
        C         2.0248665745        -0.8328065947        -0.1784282466
        C         0.6634125611        -1.0779884592        -0.2952450908
        H        -1.9382906515        -2.2527753298         0.3375785117
        H        -1.7325527068        -1.9153010279        -1.4062293601
        H        -3.2354436539        -1.4449230977        -0.5834072180
        H        -2.3258039498         1.7799352398        -0.3596699483
        H        -2.4380696896         1.1126749825         1.2952515529
        H        -3.5489309827         0.5464929087         0.0192863203
        H        -0.3186096820         2.0750027009         0.5797111017
        H         2.1115893611         2.3058327804         0.7225009980
        H         2.7275420038        -1.6481067809        -0.3786982324
        H         0.3282695482        -2.0750044893        -0.5782226136
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
