#!/bin/sh

AMS_JOBNAME="system_043_conformer_001" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        C         2.4936163872         0.0586904820         0.0118903084
        C         1.1484265278        -0.6299628561         0.2103038981
        N         0.0337067417         0.3123783945         0.0215928520
        C        -1.2755828881        -0.3573872866         0.0793875214
        C        -2.4046605309         0.6089227768        -0.2571861513
        H         3.3189986812        -0.6486211840         0.1774711934
        H         2.6119884371         0.9007445485         0.7103727246
        H         2.5875720030         0.4487843916        -1.0141234509
        H         1.0687800664        -1.4994459186        -0.4772328623
        H         1.0765023655        -1.0333019552         1.2344426068
        H         0.1304539664         0.7193088796        -0.9169839547
        H        -1.3164521616        -1.2330579674        -0.6036125586
        H        -1.4065174732        -0.7515454865         1.1011818080
        H        -2.4095308210         1.4657424531         0.4331207524
        H        -3.3792224088         0.1041612867        -0.1908636015
        H        -2.2957815504         0.9962625824        -1.2828221927
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
