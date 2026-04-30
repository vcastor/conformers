#!/bin/sh

AMS_JOBNAME="system_029_conformer_002" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        C        -2.5154608259        -0.0684720454        -0.4829104635
        C        -1.2419295553         0.3091485771         0.2746954522
        C         0.0543235057         0.0125017676        -0.4859384065
        N         0.1598972897        -1.4256137312        -0.8066202598
        C         1.2531410912         0.5364398069         0.3139345889
        O         2.5220478750         0.2264623389        -0.3053803557
        H        -3.4089042867         0.1753885681         0.1095924815
        H        -2.5377674296        -1.1437782215        -0.7073368571
        H        -2.5823702439         0.4766846839        -1.4368237241
        H        -1.2602215835         1.3833352622         0.5207001484
        H        -1.2085139826        -0.2290819023         1.2390511031
        H         0.0286271669         0.5566048766        -1.4491104927
        H         1.1232533456        -1.5988020362        -1.1181734273
        H         0.0708366142        -1.9552870544         0.0699257195
        H         1.2825784357         0.0472631190         1.2999442261
        H         1.1586302685         1.6254051800         0.4695382060
        H         2.5810526826         0.7589483239        -1.1224085356
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
