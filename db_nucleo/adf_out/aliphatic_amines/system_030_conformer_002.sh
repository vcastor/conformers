#!/bin/sh

AMS_JOBNAME="system_030_conformer_002" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        N         2.5606779190         1.1387131127         0.2299211748
        C         1.9544658092        -0.1961018507         0.0867542133
        C         0.4428950646        -0.1559449433        -0.0050535906
        C        -0.2821003810        -1.3538317248         0.1167677064
        C        -1.6751085656        -1.3622016930         0.0174834556
        C        -2.3718323525        -0.1654784726        -0.1959732447
        C        -1.6606060787         1.0324224542        -0.3099172426
        C        -0.2628520119         1.0364402533        -0.2170469994
        H         3.5757834060         1.0221923606         0.2993536871
        H         2.2753442868         1.5368712272         1.1312513701
        H         2.3508099905        -0.6422075334        -0.8414206419
        H         2.2281165680        -0.8933299113         0.9016263324
        H         0.2548333223        -2.2902018138         0.2942964174
        H        -2.2209430121        -2.3036418067         0.1131988186
        H        -3.4616398136        -0.1690270851        -0.2680033452
        H        -2.1945124558         1.9720539552        -0.4706846036
        H         0.2898816963         1.9729643797        -0.3106687552
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
