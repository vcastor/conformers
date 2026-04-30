#!/bin/sh

AMS_JOBNAME="system_033_conformer_001" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        C         2.4152275384         0.0147014497        -0.0870577955
        C         0.9107951009         0.0136540448        -0.0293326442
        C         0.1981010401         1.2175682895         0.1091965209
        C        -1.1934922736         1.1907748953         0.1541703190
        C        -1.8447229066        -0.0430263589         0.0607268980
        C        -1.0628145547        -1.1895872479        -0.0737971024
        N         0.2851803966        -1.1803172358        -0.1197049990
        H         2.7908606101        -1.0081992993        -0.2091437441
        H         2.8406684698         0.4434166161         0.8330952174
        H         2.7732141779         0.6285198180        -0.9273267379
        H         0.7399387369         2.1634819082         0.1773721938
        H        -1.7632696050         2.1165095511         0.2584867740
        H        -2.9331319187        -0.1166649482         0.0894548970
        H        -1.5370036291        -2.1727150445        -0.1540838717
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
