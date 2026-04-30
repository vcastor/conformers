#!/bin/sh

AMS_JOBNAME="system_024_conformer_007" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        O        -2.6910764775         0.8774560853         1.1122294188
        C        -2.5431732276         0.2584528537        -0.1908867713
        C        -1.1871616324         0.5294026296        -0.8215591121
        N        -0.0958560359        -0.1168530331        -0.0803563716
        C         1.2050116681         0.0978085471        -0.7327186437
        C         2.3440190104        -0.4162315921         0.1221276129
        O         2.3987706233         0.3917221625         1.3249693982
        H        -2.2811315219         0.2803803990         1.7659419121
        H        -2.7150084412        -0.8274034171        -0.1123447313
        H        -3.3301944251         0.6920363356        -0.8234216975
        H        -1.2009563636         0.1176317216        -1.8443162603
        H        -1.0398651492         1.6256770570        -0.9135570195
        H        -0.0367449512         0.3264074200         0.8433209874
        H         1.3848075826         1.1695894060        -0.9614092758
        H         1.2150298246        -0.4442712885        -1.6913933190
        H         3.2912776033        -0.3359495086        -0.4366542840
        H         2.1752143253        -1.4741264346         0.3847526693
        H         3.0463097166        -0.0265612572         1.9230748617
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
