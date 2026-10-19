#!/bin/sh

AMS_JOBNAME="system_019_conformer_004" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        N         1.5674263665         0.0246494123        -0.0880735504
        C         0.3055253934         0.3041374638        -0.8003308972
        C        -0.8003836270        -0.6177971834        -0.3169856996
        O        -1.0807830064        -0.4479392420         1.0947451949
        H         2.2693733717         0.7129091096        -0.3769336340
        H         1.4116607044         0.2099863718         0.9090049014
        H        -0.0325160679         1.3541604030        -0.6934787499
        H         0.4562824651         0.1210456728        -1.8761867108
        H        -1.7132135323        -0.4523756678        -0.9127339688
        H        -0.4947586300        -1.6681066466        -0.4259955648
        H        -1.4336621852         0.4567007436         1.2062418165
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
