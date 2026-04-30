#!/bin/sh

AMS_JOBNAME="system_008_conformer_001" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        C         2.3862749405        -0.0879816369        -0.4661192945
        C         0.9226423178        -0.1268362545        -0.1064009948
        N         0.2734322111        -1.2548101172        -0.1577026702
        C        -1.1587655685        -1.1911192518         0.1759847394
        C        -1.8045490029         0.1431065261        -0.2067557448
        C        -1.0463358856         1.2778034458         0.4728517746
        N         0.3960084864         1.0778165454         0.2876151667
        H         2.5560140739         0.5807758560        -1.3240942542
        H         2.7291959246        -1.0953065567        -0.7248405076
        H         2.9845095668         0.2933182728         0.3750243633
        H        -1.6655837392        -2.0220563248        -0.3383079623
        H        -1.2919842860        -1.3686855890         1.2598162434
        H        -1.7587490383         0.2675791736        -1.3005114556
        H        -2.8624272456         0.1665499059         0.0907560850
        H        -1.2843067867         1.3016189577         1.5496031395
        H        -1.3213768115         2.2544867324         0.0516274495
        H         0.9617834053         1.9028062539         0.1099219670
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
