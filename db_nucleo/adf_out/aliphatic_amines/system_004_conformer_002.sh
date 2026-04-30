#!/bin/sh

AMS_JOBNAME="system_004_conformer_002" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        C         1.6433524113         0.3827940930        -0.3413108458
        C         0.3173311683        -0.1467985608        -0.8917169679
        C        -0.8973373982         0.1996742607        -0.0192450347
        N        -0.9183482725        -0.3890574056         1.3364049563
        H         2.4799369159         0.1359671323        -1.0108302269
        H         1.6134722557         1.4783168278        -0.2293529290
        H         1.8764323508        -0.0491834229         0.6442762398
        H         0.3707323188        -1.2433093380        -1.0098927902
        H         0.1447063662         0.2668020038        -1.9000027247
        H        -1.8164879427        -0.1199866894        -0.5347901148
        H        -0.9641145674         1.2949382436         0.0934941116
        H        -0.8182393687        -1.4073442402         1.2527569198
        H        -0.0804174431        -0.0867945657         1.8447215556
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
