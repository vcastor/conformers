#!/bin/sh

AMS_JOBNAME="system_044_conformer_001" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        C         1.3660354951         0.2522884801        -0.3240823938
        C         0.8745392495        -1.0667201918         0.2553987373
        O        -0.4949959149        -1.3278387173        -0.1233125862
        C        -1.3435688265        -0.2455366609         0.3198582462
        C        -0.8873352602         1.0870852307        -0.2569735420
        N         0.5010431899         1.3399231028         0.1653139771
        H         1.3614636100         0.1792762606        -1.4317649527
        H         2.4010539157         0.4315208036         0.0032166896
        H         1.4671192969        -1.9086148200        -0.1258479326
        H         0.9487919233        -1.0417348038         1.3594756618
        H        -2.3596109440        -0.4912118575        -0.0157764869
        H        -1.3280564883        -0.2001386787         1.4257282353
        H        -1.5373349454         1.8898679825         0.1222282287
        H        -0.9897615317         1.0520900352        -1.3617851826
        H         0.8155673232         2.2227484537        -0.2462651409
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
