#!/bin/sh

AMS_JOBNAME="system_016_conformer_001" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        C         1.3660221158         0.2521761838        -0.3241487461
        C         0.8750520707        -1.0667575990         0.2555092607
        O        -0.4951184352        -1.3281718218        -0.1232894260
        C        -1.3439822538        -0.2452312855         0.3200179890
        C        -0.8874037455         1.0869874708        -0.2570583763
        N         0.5011869184         1.3403074698         0.1654273295
        H         1.3607181945         0.1796587347        -1.4317465820
        H         2.4012202151         0.4312039417         0.0025141676
        H         1.4677435790        -1.9084423708        -0.1258173911
        H         0.9487738075        -1.0421227933         1.3595440981
        H        -2.3599911389        -0.4907067516        -0.0156320249
        H        -1.3282353404        -0.2004186643         1.4258177765
        H        -1.5376786050         1.8897845262         0.1214889583
        H        -0.9889161614         1.0518365347        -1.3618318692
        H         0.8153362241         2.2222662973        -0.2484896646
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
