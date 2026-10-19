#!/bin/sh

AMS_JOBNAME="system_026_conformer_003" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        N         2.5954767940         0.1096422440        -0.2110621578
        C         1.2853035500        -0.5215305509         0.0463989034
        C         0.0641273411         0.3777469676        -0.1713249806
        C        -1.2502398990        -0.3415281452         0.1211485919
        N        -2.4093917705         0.5374902475        -0.1493240782
        H         2.5959302317         0.4777438686        -1.1692649476
        H         2.6780172116         0.9423141619         0.3833731905
        H         1.2889461973        -0.8935220887         1.0838355759
        H         1.2052695320        -1.4084354828        -0.6034619808
        H         0.0560210088         0.7433412902        -1.2125121606
        H         0.1485138448         1.2660757639         0.4803210640
        H        -1.3385785100        -1.2236427384        -0.5336538370
        H        -1.2325304098        -0.7169160106         1.1627416145
        H        -3.2679297733         0.0301275356         0.0899213583
        H        -2.3812416644         1.3214002516         0.5128168250
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
