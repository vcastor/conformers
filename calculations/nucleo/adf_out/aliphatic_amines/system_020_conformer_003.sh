#!/bin/sh

AMS_JOBNAME="system_020_conformer_003" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        N         1.4681567342        -0.9347826837         0.2928358290
        C         0.5850427248        -0.3749014205        -0.7486305695
        C        -0.3826563920         0.7103308324        -0.2682658043
        N        -1.2696928072         0.1781251994         0.7866963691
        H         2.0862581667        -0.1851571174         0.6247812343
        H         0.8758411541        -1.1511694867         1.1041855466
        H         1.2084395095         0.0328770086        -1.5586403742
        H         0.0007590139        -1.2036732396        -1.1849937494
        H        -0.9322107033         1.1070682983        -1.1440470475
        H         0.1935497372         1.5452623418         0.1625225449
        H        -1.8498718513         0.9393646300         1.1517933577
        H        -1.9335165886        -0.4758657769         0.3571084703
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
