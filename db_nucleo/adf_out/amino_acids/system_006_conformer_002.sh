#!/bin/sh

AMS_JOBNAME="system_006_conformer_002" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        N         0.1997405020        -1.7819336033        -0.0900184321
        C         0.5623404398        -0.5404177413        -0.5481144395
        C         1.5626521109         0.1952415845         0.3389992012
        O         1.1983775957         0.1289021237         1.7178223733
        C        -0.9364170270         0.5176367113        -0.5545487670
        O        -1.1222598398         1.0328614155         0.5563069223
        O        -1.4704368372         0.4769528462        -1.6606802127
        H        -0.3166886972        -2.4158323506        -0.6942884475
        H         0.0852611017        -1.9108886346         0.9152462029
        H         0.8090673567        -0.5313484845        -1.6143724750
        H         1.6673818621         1.2333990900        -0.0114197072
        H         2.5359792297        -0.3087650386         0.2356540574
        H         0.3261529749         0.5907485956         1.7561735795
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
