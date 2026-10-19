#!/bin/sh

AMS_JOBNAME="system_057_conformer_004" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        O         2.0227596985         0.1628960375         0.9532938967
        C         1.6296308677         0.4283440613        -0.4122529140
        C         0.1419990869         0.1989218976        -0.6584008832
        C        -0.8134347865         1.1698679705         0.1084564289
        C        -1.8847885420         0.2561712576         0.7477256188
        C        -1.6923375417        -1.0908447932         0.0230360918
        N        -0.2496252845        -1.1843580808        -0.2887376974
        H         1.6152409552         0.8528254487         1.5125154468
        H         1.8986073922         1.4579209643        -0.7012801372
        H         2.2212907283        -0.2674146666        -1.0235936841
        H        -0.0237926736         0.3216506452        -1.7423761701
        H        -1.2579987361         1.8930992415        -0.5892315206
        H        -0.2781028153         1.7537971482         0.8734010014
        H        -1.6886012181         0.1268262426         1.8227886648
        H        -2.9038915300         0.6536768383         0.6386453651
        H        -2.2554195802        -1.0985108321        -0.9251310620
        H        -2.0136750754        -1.9585016830         0.6149803464
        H         0.2363286890        -1.3828691285         0.5963437480
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
