#!/bin/sh

AMS_JOBNAME="system_026_conformer_006" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        N         2.4825887274         0.2546643200        -0.3805487209
        C         1.2445420178        -0.4553321438         0.0058569881
        C         0.0168241454         0.4083909033        -0.2696363935
        C        -1.2876320573        -0.2991981208         0.0864739168
        N        -2.4519911947         0.5573745926        -0.2248345224
        H         3.2861801025        -0.3422561576        -0.1587592936
        H         2.5920268727         1.0699953716         0.2334616919
        H         1.2412309904        -0.7638569321         1.0694692745
        H         1.1842181366        -1.3786429677        -0.5933358754
        H         0.0936836604         1.3424335876         0.3171328764
        H         0.0008809396         0.6991688610        -1.3332195044
        H        -1.2549660528        -0.6092847436         1.1491162955
        H        -1.3796030116        -1.2209803443        -0.5110972167
        H        -3.3062697468         0.0604191869         0.0480370724
        H        -2.4240198454         1.3774119012         0.3918363920
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
