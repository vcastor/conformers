#!/bin/sh

AMS_JOBNAME="system_027_conformer_001" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        C         2.4056315816         0.4967599128        -0.0003296658
        C         0.9274610579         0.2171323819         0.0042546767
        C        -0.0160740128         1.2278719012         0.2392178943
        C        -1.3740949746         0.9137537304         0.2332238672
        C        -1.7580667266        -0.4081067017        -0.0074794422
        N        -0.8775110620        -1.4002204243        -0.2367011788
        C         0.4294053071        -1.0734538120        -0.2267663374
        H         2.7396158948         0.8641644607         0.9822412504
        H         2.6565984288         1.2728174755        -0.7393918669
        H         2.9805270571        -0.4072602800        -0.2419228576
        H         0.3138643188         2.2536685095         0.4242754259
        H        -2.1308806052         1.6798907910         0.4120936899
        H        -2.8169572152        -0.6837690294        -0.0197710598
        H         1.1318405937        -1.8935136450        -0.4133305410
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
