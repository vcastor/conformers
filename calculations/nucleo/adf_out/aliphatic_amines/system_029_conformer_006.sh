#!/bin/sh

AMS_JOBNAME="system_029_conformer_006" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        C        -2.4421179853        -0.1328702768        -0.5169835754
        C        -1.1570188121         0.0708994279         0.2862474176
        C         0.1229016475        -0.0243160684        -0.5473339391
        N         0.2467038309        -1.3681815270        -1.1504850509
        C         1.3677805695         0.3279766536         0.2823394921
        O         1.3494102691         1.6588757582         0.8438463721
        H        -2.4692644640        -1.1314177913        -0.9748491357
        H        -2.5212801029         0.6099474444        -1.3260440420
        H        -3.3282561293        -0.0263373772         0.1251309542
        H        -1.0968971152        -0.6756883536         1.0991326287
        H        -1.1688336472         1.0583787044         0.7723258222
        H         0.0534265448         0.6992230553        -1.3811614854
        H         1.1487395472        -1.4363892838        -1.6348554529
        H         0.2964620011        -2.0608004591        -0.3933439511
        H         2.2702044512         0.1880749957        -0.3391626342
        H         1.4398647446        -0.3564051673         1.1424611084
        H         1.3673950179         2.2861777781         0.0954148748
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
