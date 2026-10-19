#!/bin/sh

AMS_JOBNAME="system_005_conformer_002" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        C         1.6795072766         0.0512836508        -0.1292164821
        N         0.7323935776         0.1944703852         0.9959225469
        N        -0.6728813008         0.2862717632         0.6382223856
        C        -0.9528552714         1.2264785936        -0.4574691248
        C        -1.1799961292        -1.0499175119         0.3224865373
        H         2.6881771719        -0.0094013844         0.3016293293
        H         1.6619481672         0.8830305635        -0.8548190507
        H         1.4866383286        -0.8883818054        -0.6646970933
        H         0.9392303930         1.0758771737         1.4756228436
        H        -0.5579218924         0.8970417698        -1.4387684900
        H        -2.0425891365         1.3335338938        -0.5499694297
        H        -0.5269082699         2.2102352373        -0.2153388000
        H        -0.9783203121        -1.7224088470         1.1660752411
        H        -0.7331368765        -1.4845404740        -0.5957542447
        H        -2.2657983340        -0.9859751302         0.1669874974
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
