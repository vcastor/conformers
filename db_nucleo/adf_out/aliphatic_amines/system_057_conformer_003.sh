#!/bin/sh

AMS_JOBNAME="system_057_conformer_003" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        O         2.4562820500        -0.2306026208        -1.0002189943
        C         1.6084330218         0.6417162016        -0.2195889499
        C         0.1371963704         0.3302379337        -0.4139344864
        C        -0.8254125492         1.2574254980         0.3645805306
        C        -2.0393041904         0.3504944909         0.7072108537
        C        -1.6483087759        -1.0462777339         0.1541205596
        N        -0.1705168229        -1.0533867286         0.0277708112
        H         2.0543745300        -1.1204491763        -0.9151281388
        H         1.8293135475         1.6687763246        -0.5417033270
        H         1.8610954345         0.5579798716         0.8561833063
        H        -0.0968051161         0.3800166671        -1.4924026540
        H        -0.3349243931         1.6185542538         1.2825719789
        H        -1.1065985335         2.1373248966        -0.2302743389
        H        -2.1964096924         0.3047870038         1.7942660394
        H        -2.9715292227         0.7164876742         0.2541688309
        H        -2.0780680536        -1.1951309724        -0.8493008134
        H        -1.9802647682        -1.8780198059         0.7896117118
        H         0.2056367983        -1.1464352089         0.9822496205
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
