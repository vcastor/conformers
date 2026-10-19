#!/bin/sh

AMS_JOBNAME="system_041_conformer_008" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        C         2.1552951571         0.1805542098        -0.3437746379
        C         1.2001840491        -0.1790132587         0.7964438338
        C        -0.1363580806         0.5727617064         0.7438927646
        C        -0.9934661298         0.2864771729        -0.4901884893
        N        -1.3485231627        -1.1472498254        -0.5779676799
        H         1.7425783631        -0.1020211970        -1.3237506148
        H         2.3536264617         1.2640625124        -0.3661315137
        H         3.1199258799        -0.3356351586        -0.2313070173
        H         1.0043824299        -1.2629404901         0.7857376638
        H         1.6863715324         0.0408914727         1.7608270249
        H         0.0508385864         1.6593977525         0.7871715480
        H        -0.7271540114         0.3260898152         1.6438150077
        H        -1.8828566051         0.9441503248        -0.4605318404
        H        -0.4387799420         0.5485369007        -1.4048354522
        H        -1.9750334330        -1.2808914799        -1.3783000485
        H        -1.9189905405        -1.3883759646         0.2406332828
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
