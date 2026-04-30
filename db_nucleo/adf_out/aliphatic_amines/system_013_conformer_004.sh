#!/bin/sh

AMS_JOBNAME="system_013_conformer_004" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        C         2.0246927438         0.0569836351        -0.4171883060
        C         1.0176091858        -0.2540021719         0.6872310881
        N        -0.0807960425        -1.1209043365         0.2133204060
        C        -1.0680940364        -0.4499746860        -0.6568632458
        C        -1.8549744842         0.7026112498        -0.0215244509
        H         2.4414492957        -0.8716644063        -0.8344761861
        H         1.5659851621         0.6260748533        -1.2387843265
        H         2.8517741827         0.6615614207        -0.0181017050
        H         1.5237661686        -0.7989816804         1.4982749972
        H         0.6518377048         0.6946780940         1.1267663563
        H        -0.5827061715        -1.4637344196         1.0389044286
        H        -0.5438808452        -0.0916897018        -1.5561304963
        H        -1.7731878913        -1.2234090966        -0.9994587171
        H        -1.2008379773         1.5339819432         0.2778141061
        H        -2.3985546008         0.3560115486         0.8710041367
        H        -2.5921761142         1.1002094262        -0.7351372315
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
