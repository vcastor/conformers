#!/bin/sh

AMS_JOBNAME="system_003_conformer_004" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        C         2.6534478983         0.3734649349        -0.1945889332
        C         1.6416125916        -0.5623497121        -0.8265955072
        O         0.2805634340        -0.0363203806        -0.6515263247
        C        -0.3748936180        -0.4158234290         0.4657236891
        O         0.0726650753        -1.1907330816         1.3079451903
        C        -1.7698657828         0.1741810273         0.5410518614
        N        -1.9502425192         1.3994306309        -0.2489728082
        H         3.6675217391        -0.0050559509        -0.3868189097
        H         2.5078474333         0.4343933737         0.8927011972
        H         2.5736899147         1.3823149538        -0.6226583098
        H         1.6836171973        -1.5683109243        -0.3917033505
        H         1.7641734964        -0.6234813358        -1.9142316624
        H        -2.4475909702        -0.6564390779         0.2572854839
        H        -1.9648405318         0.3882699821         1.6004749451
        H        -1.8102129940         1.1822175726        -1.2402756717
        H        -2.9317991325         1.6816324815        -0.1695684527
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
