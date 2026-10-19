#!/bin/sh

AMS_JOBNAME="system_001_conformer_001" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        C         2.2488315567        -0.4277432160        -0.3442710376
        C         0.7596610902        -0.3502347459        -0.2259619419
        N        -0.0487300150        -1.2439616558        -0.6541392210
        C        -1.4581794193        -0.9293699443        -0.4108989273
        C        -1.6327951169         0.4382530187         0.3192016465
        S         0.0621898380         1.0973278563         0.5741274614
        H         2.5349391555        -1.3591301276        -0.8464968119
        H         2.6320211361         0.4299560025        -0.9165974321
        H         2.7145399068        -0.3911891060         0.6518596037
        H        -1.8976696296        -1.7438825550         0.1851044089
        H        -1.9845777193        -0.9215203053        -1.3776882505
        H        -2.2015718642         1.1579664214        -0.2804423264
        H        -2.1162008369         0.3257801311         1.2963157736
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
