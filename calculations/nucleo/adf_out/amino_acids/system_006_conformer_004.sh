#!/bin/sh

AMS_JOBNAME="system_006_conformer_004" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        N        -0.1515582975        -1.5947628434         0.3247334391
        C         0.3090811917        -0.5023173713        -0.3735829260
        C         1.3645080647         0.3328600836         0.3586538276
        O         2.6444660843        -0.3031347089         0.2734030305
        C        -1.0214846491         0.7058126442        -0.6150385735
        O        -1.1665021374         0.9115364320        -1.8219966396
        O        -1.4893000763         1.0650708736         0.4655591087
        H        -0.6205954660        -2.3438646967        -0.1794806125
        H        -0.4616152451        -1.4614001496         1.2873496296
        H         0.5888864651        -0.7580530065        -1.3995505338
        H         1.4754453761         1.3101832555        -0.1241888580
        H         1.0493511882         0.4817965857         1.4039412730
        H         2.5804682735        -1.1571705841         0.7469576905
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
