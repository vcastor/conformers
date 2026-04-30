#!/bin/sh

AMS_JOBNAME="system_025_conformer_003" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        C         2.2532779676         0.2236150474         0.2547313237
        O         0.9247272230         0.0066927538        -0.3046999176
        C        -0.0940055422         0.1283963623         0.5722688403
        O         0.0560655832         0.4025096322         1.7605966890
        C        -1.4545545879        -0.0671914282        -0.0667449107
        N        -1.4211609043        -0.6265653209        -1.4231873263
        H         2.3234606652         1.2344517174         0.6741412106
        H         2.4567117961        -0.5207677205         1.0338125785
        H         2.9413493683         0.1028643912        -0.5864143643
        H        -1.9542687666         0.9181404824         0.0118070020
        H        -2.0096903430        -0.7481523983         0.5946360410
        H        -2.3898296449        -0.7261742506        -1.7420385204
        H        -1.0034112736         0.0607716252        -2.0584384729
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
