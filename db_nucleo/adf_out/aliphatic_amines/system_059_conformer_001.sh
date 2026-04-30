#!/bin/sh

AMS_JOBNAME="system_059_conformer_001" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        F         0.7537957551         1.5166786596        -0.2747670844
        C         1.0815507460         0.2068029466        -0.0130772872
        F         1.8603356565         0.2195013747         1.1211536801
        F         1.8962357227        -0.2125706713        -1.0427065153
        C        -0.1391501538        -0.6997533614         0.1354969880
        C        -1.0068012958        -0.7479734853        -1.1554183392
        C        -2.4468837666        -0.6924469299        -0.6208807227
        C        -2.2961541061         0.1839176074         0.6270755138
        N        -1.0016838144        -0.2149447003         1.2391541108
        H         0.2678065150        -1.6916983956         0.3776869129
        H        -0.7964915379        -1.6455674791        -1.7484154803
        H        -0.8059656021         0.1304773230        -1.7855948195
        H        -3.1523205108        -0.2829877463        -1.3572162503
        H        -2.7921032597        -1.6981167422        -0.3339378694
        H        -2.2491419617         1.2474543867         0.3431720272
        H        -3.1049330013         0.0629439964         1.3589155847
        H        -1.1757578245        -1.0069862545         1.8612859362
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
