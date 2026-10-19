#!/bin/sh

AMS_JOBNAME="system_006_conformer_001" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        C         2.9327723317        -0.0677319457         0.2418396128
        C         1.4284813172        -0.0440263929         0.1379263749
        C         0.7239797727        -1.0714939606        -0.5104668663
        C        -0.6652529657        -1.0393044689        -0.6425342636
        C        -1.4097443004         0.0371876830        -0.1244835997
        N        -2.7982047969         0.1141853529        -0.3196509995
        C        -0.7141565057         1.0659074167         0.5380004388
        C         0.6755642582         1.0191106494         0.6620790362
        H         3.3138174569        -1.0973344516         0.3016142322
        H         3.2805466428         0.4812951580         1.1283431797
        H         3.4009205097         0.4028030929        -0.6390322931
        H         1.2744668387        -1.9234808691        -0.9195523619
        H        -1.1845775666        -1.8560905750        -1.1514266056
        H        -3.2794635807         0.6600776779         0.3952176839
        H        -3.2462324741        -0.7966348438        -0.4209956289
        H        -1.2718955953         1.9070729095         0.9586680562
        H         1.1874951896         1.8313107700         1.1862377078
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
