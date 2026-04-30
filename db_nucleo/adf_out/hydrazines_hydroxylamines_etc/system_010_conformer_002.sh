#!/bin/sh

AMS_JOBNAME="system_010_conformer_002" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        C         2.3251389478        -0.4719336726         0.7642708731
        N         1.5146994158         0.5444675399         0.7245436221
        N         0.4008352395         0.4835968151        -0.0191605998
        C        -0.6492935404         1.4956830686         0.2155797768
        C        -1.9528509760         0.7063156398         0.0502026086
        C        -1.5709387162        -0.3870615314        -0.9619784466
        C        -0.1538619268        -0.7765683686        -0.5339036551
        H         2.1634025777        -1.4127261514         0.2247452957
        H         3.2269034796        -0.3547107132         1.3660852959
        H        -0.5235909713         1.9371084360         1.2126828558
        H        -0.5737466953         2.3010682157        -0.5349437945
        H        -2.7865305316         1.3354691086        -0.2864633694
        H        -2.2344818403         0.2447527867         1.0092585493
        H        -1.5513246973         0.0279824053        -1.9813911979
        H        -2.2558366740        -1.2443970871        -0.9552614599
        H         0.4559774612        -1.1736673541        -1.3600915180
        H        -0.1579851479        -1.5343028719         0.2758319639
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
