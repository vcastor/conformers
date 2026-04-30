#!/bin/sh

AMS_JOBNAME="system_029_conformer_008" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        C        -2.4386372393         0.0304871309        -0.5643452769
        C        -1.1439905153         0.1232045791         0.2457136389
        C         0.1170575117         0.2122650694        -0.6265100109
        N         0.2678503412        -1.0223798845        -1.4247562178
        C         1.3657128652         0.5562578414         0.1999061685
        O         1.7576592223        -0.4945626618         1.1129911438
        H        -2.5599249480         0.9163013147        -1.2073839598
        H        -2.4298194708        -0.8565914654        -1.2121727089
        H        -3.3171538773        -0.0318045687         0.0939163920
        H        -1.1766511090         1.0089136276         0.9009485209
        H        -1.0627369394        -0.7570229216         0.9085185321
        H        -0.0183626004         1.0486096938        -1.3356699481
        H         1.0934186343        -0.9236700844        -2.0261294703
        H         0.5104045512        -1.7796357184        -0.7739825283
        H         2.2257129924         0.6900204307        -0.4725336987
        H         1.2070558687         1.5023870650         0.7477314957
        H         1.0816250801        -0.5356319346         1.8164373312
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
