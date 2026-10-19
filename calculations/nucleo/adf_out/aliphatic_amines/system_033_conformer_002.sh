#!/bin/sh

AMS_JOBNAME="system_033_conformer_002" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        N         1.4666495342         0.6084913805        -0.0605546839
        C         0.3138046666         0.3342267178        -0.9374384114
        C        -0.7621288516        -0.5814747018        -0.3607665201
        O        -1.4433068195        -0.0066715794         0.7795445106
        H         1.1477139070         1.0877151064         0.7878745638
        H         1.8721014631        -0.2788846257         0.2573320756
        H        -0.1439561782         1.2977680634        -1.2103942693
        H         0.6848626824        -0.1236836274        -1.8687131098
        H        -0.3233456254        -1.5569299409        -0.0854457540
        H        -1.5422090809        -0.7581426145        -1.1155914733
        H        -0.8195676554        -0.0315178753         1.5304998983
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
