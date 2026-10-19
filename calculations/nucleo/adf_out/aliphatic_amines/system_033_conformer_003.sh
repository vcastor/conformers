#!/bin/sh

AMS_JOBNAME="system_033_conformer_003" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        N         1.5599052696         0.6561513729        -0.0965958272
        C         0.3746846204         0.3789997117        -0.9301177368
        C        -0.6719240251        -0.5244520240        -0.2970524981
        O        -1.1985530042         0.1515421446         0.8709083235
        H         2.0264679765        -0.2338700253         0.1126635884
        H         1.2331996690         0.9969320694         0.8145831301
        H         0.7041411385        -0.0802768984        -1.8743193183
        H        -0.0982991827         1.3406875905        -1.1878316433
        H        -0.2154120538        -1.4866702416        -0.0044523436
        H        -1.4810822447        -0.7270689114        -1.0211376536
        H        -1.7825101213        -0.4810784852         1.3296988056
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
