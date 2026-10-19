#!/bin/sh

AMS_JOBNAME="system_001_conformer_002" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        C         1.7465965334        -1.3451744202         0.0183315445
        C         2.2848946015         0.0566939772        -0.2283538971
        S         1.1471116065         1.3287793426         0.4523542473
        C        -0.4136502746         0.6056136971         0.0515663453
        N        -1.5166387962         1.2129223567         0.3830659455
        C        -2.6084777517         0.3911975269        -0.1984756465
        C        -1.9553506791        -0.9439171442        -0.6151851499
        N        -0.5285221152        -0.5715945956        -0.6619763001
        C         0.4862548472        -1.6212407914        -0.7958876540
        H         2.5092216225        -2.0842412397        -0.2707917006
        H         1.5449567759        -1.4781230490         1.0919584036
        H         3.2326482349         0.2289702375         0.2968105896
        H         2.4383363202         0.2488233913        -1.2994731925
        H        -3.0236768537         0.9177387618        -1.0746894152
        H        -3.4228889519         0.2528690318         0.5251385443
        H        -2.1040353489        -1.7423027954         0.1355189706
        H        -2.2996403194        -1.3121569763        -1.5909642679
        H         0.7468243712        -1.7392554627        -1.8614975966
        H         0.0362722597        -2.5720889403        -0.4667514445
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
