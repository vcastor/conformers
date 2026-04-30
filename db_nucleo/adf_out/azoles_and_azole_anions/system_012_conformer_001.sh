#!/bin/sh

AMS_JOBNAME="system_012_conformer_001" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        C        -2.2461821580         0.2174281497         0.0776550277
        C        -1.9465244288        -1.1347522073        -0.2030216111
        C        -0.6293898908        -1.5832772355        -0.3150494447
        C         0.3756682408        -0.6278991296        -0.1341246945
        N         1.7570490998        -0.7009551503        -0.1643695936
        C         2.2388007209         0.5574106898         0.0807204168
        N         1.2836071077         1.4547831373         0.2765219760
        C         0.0932256669         0.7368686175         0.1476630916
        C        -1.2385867724         1.1658842578         0.2546740326
        H        -3.2912798868         0.5233409127         0.1566980845
        H        -2.7645455131        -1.8455835747        -0.3354041878
        H        -0.3988178752        -2.6280715760        -0.5308797168
        H         2.3190399947        -1.5306649605        -0.3365969774
        H         3.3073686251         0.7585802155         0.1077786298
        H        -1.4720195790         2.2108125649         0.4700082707
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
