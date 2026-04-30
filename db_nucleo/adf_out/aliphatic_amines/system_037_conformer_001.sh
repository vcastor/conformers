#!/bin/sh

AMS_JOBNAME="system_037_conformer_001" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        N         1.5921483765         0.4205082419        -0.0624041375
        C         0.3517774449         0.3481886321        -0.8534902592
        C        -0.7314260600        -0.5703424109        -0.2919748076
        O        -1.1322891906        -0.2010440772         1.0483111979
        H         2.0050445388        -0.5184290880        -0.0165911902
        H         1.3343404264         0.6353440283         0.9079829314
        H         0.5969537528         0.0076034489        -1.8724487657
        H        -0.0559858887         1.3690798607        -0.9520451400
        H        -1.6035381546        -0.5777701415        -0.9700281340
        H        -0.3520731885        -1.6000030909        -0.2076043234
        H        -1.5529366431         0.6790051531         0.9871388591
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
