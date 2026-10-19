#!/bin/sh

AMS_JOBNAME="system_005_conformer_002" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        C         1.4194647242         0.3299342000         0.2123908841
        C         0.8686873570        -1.0482791961        -0.1427438550
        O        -0.4486670313        -1.2440664937         0.4167316297
        C        -1.3475792881        -0.2271380934        -0.0782589629
        C        -0.8499955287         1.1702756986         0.2800353752
        N         0.5240424254         1.4326785770        -0.1954936125
        H         2.4028590009         0.4705611469        -0.2610629812
        H         1.5597548253         0.3931844724         1.3044748218
        H         1.5010584391        -1.8491631611         0.2658413530
        H         0.8149859782        -1.1633170792        -1.2437313022
        H        -2.3275705600        -0.4313494872         0.3758499210
        H        -1.4367271626        -0.3274596947        -1.1783193720
        H        -1.5277481668         1.9262192630        -0.1442497662
        H        -0.8582137485         1.2874763498         1.3766622276
        H         0.5006272552         1.4535914037        -1.2226353534
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
