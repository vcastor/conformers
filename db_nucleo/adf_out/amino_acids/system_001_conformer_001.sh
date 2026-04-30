#!/bin/sh

AMS_JOBNAME="system_001_conformer_001" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        N        -1.9996292771         0.0888800874        -0.0799469196
        C        -0.9406207959        -0.2667144125         0.6938864078
        C         0.7676120368         0.0200130774        -0.0892331244
        O         0.6788483430         0.3354452392        -1.2684135611
        O         1.5901632979        -0.2012967044         0.7957360210
        H        -2.2668259655         1.0677821194        -0.1512286435
        H        -2.2751673068        -0.4995890152        -0.8626204217
        H        -0.8002031338         0.3509979389         1.5832015150
        H        -0.8249681250        -1.3439961621         0.8395175876
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
