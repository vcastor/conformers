#!/bin/sh

AMS_JOBNAME="system_026_conformer_002" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        N         2.3329766195         0.2667043326        -0.6349719948
        C         1.0804605621        -0.3097742180        -0.1028567289
        C        -0.2084398579         0.3928692229        -0.5428779403
        C        -1.4880105124        -0.2555756803         0.0052710251
        N        -1.6902298607        -0.1742582592         1.4674420648
        H         2.2673113558         0.2951229767        -1.6591201743
        H         2.3815507992         1.2531451420        -0.3549645730
        H         1.0386163039        -1.3682929336        -0.4098416777
        H         1.1576839712        -0.3048783132         0.9963511951
        H        -0.1739855177         1.4525001694        -0.2313532682
        H        -0.2563377493         0.3871514035        -1.6461918518
        H        -1.5057210155        -1.3219344609        -0.2751632777
        H        -2.3619428431         0.2086853104        -0.4774040487
        H        -0.9055809127        -0.6313043457         1.9435394757
        H        -1.6306576580         0.8101469679         1.7520947557
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
