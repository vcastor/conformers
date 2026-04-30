#!/bin/sh

AMS_JOBNAME="system_026_conformer_008" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        N         1.5198475619        -0.3439091399         1.3822089215
        C         1.3542190238        -0.4077436434        -0.0881828537
        C         0.1224579458         0.3752307391        -0.5438055272
        C        -1.1988172953        -0.1958173184        -0.0207404941
        N        -2.4137720626         0.5337845037        -0.4396281984
        H         2.3762021900        -0.8476041319         1.6350870649
        H         1.7088942515         0.6312672890         1.6411784513
        H         1.2356159203        -1.4684340314        -0.3652097459
        H         2.2408587392        -0.0327397886        -0.6327937541
        H         0.1011566854         0.3870255139        -1.6466814735
        H         0.2186841088         1.4280228844        -0.2209912440
        H        -1.2980066443        -1.2413084389        -0.3573741515
        H        -1.1787621171        -0.2202723470         1.0785146718
        H        -2.3309408162         1.5080868774        -0.1271119811
        H        -2.4199438067         0.5947183464        -1.4645167050
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
