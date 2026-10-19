#!/bin/sh

AMS_JOBNAME="system_037_conformer_004" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        N         1.5673681549         0.0246784276        -0.0900768287
        C         0.3059495059         0.3044545240        -0.8020817639
        C        -0.7995544103        -0.6174685863        -0.3170627591
        O        -1.0779023678        -0.4468403128         1.0944189029
        H         2.2675001195         0.7181465015        -0.3705100476
        H         1.4079894163         0.1986226643         0.9084462142
        H        -0.0327054405         1.3545649231        -0.6956326876
        H         0.4559517145         0.1212304406        -1.8781167517
        H        -1.7130331583        -0.4531650596        -0.9123669818
        H        -0.4932764282        -1.6676229835        -0.4257926938
        H        -1.4362716921         0.4555400175         1.2056216281
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
