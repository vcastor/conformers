#!/bin/sh

AMS_JOBNAME="system_007_conformer_002" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        C        -1.9501057637         0.5001034341        -0.8244174267
        C        -1.1194256039         0.7228062296         0.4322181219
        O        -1.3243669369        -0.2839516158         1.4320305444
        C         0.3848842588         0.8841369865         0.1462346285
        N         1.1636904564         0.9851432353         1.2700274730
        C         0.8695300952        -0.6393251430        -0.7405543246
        O         0.4568578163        -1.6488987647        -0.1531317203
        O         1.5269635508        -0.3513538470        -1.7379946028
        H        -3.0150250846         0.4889850549        -0.5591714188
        H        -1.7816282008         1.3132706913        -1.5450643458
        H        -1.7042716905        -0.4558527133        -1.3076696235
        H        -1.4238655624         1.6734298440         0.9028294575
        H        -0.9095201067        -1.0971987220         1.0506332743
        H         0.6237265040         1.6431837119        -0.6049975566
        H         2.1249072435         1.3077663101         1.1972997961
        H         0.9333350404         0.3949692747         2.0693372517
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
