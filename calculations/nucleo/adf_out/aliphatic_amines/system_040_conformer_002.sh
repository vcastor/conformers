#!/bin/sh

AMS_JOBNAME="system_040_conformer_002" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        C         1.6433412778         0.3828062957        -0.3413051141
        C         0.3173072365        -0.1468017078        -0.8917105486
        C        -0.8973441225         0.1996993853        -0.0192180412
        N        -0.9183195728        -0.3891749492         1.3363760682
        H         2.4799798004         0.1358020180        -1.0107148579
        H         1.6134931302         1.4783596235        -0.2295544011
        H         1.8762497759        -0.0490001052         0.6444048692
        H         0.3706805513        -1.2433330560        -1.0097997502
        H         0.1446789482         0.2667873380        -1.9000129414
        H        -1.8165109843        -0.1198677674        -0.5347956463
        H        -0.9640263207         1.2949622209         0.0936242767
        H        -0.8180102086        -1.4074390108         1.2525859075
        H        -0.0804297549        -0.0868058872         1.8447126199
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
