#!/bin/sh

AMS_JOBNAME="system_014_conformer_001" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        C         0.2376759044        -1.2830337977         0.1416084068
        C         1.3025899729        -0.1545904762         0.0490500479
        C         0.4842634065         1.1219415291        -0.2724947435
        N        -0.9050854972         0.8683048899         0.1757850282
        C        -1.1084264471        -0.5662976000        -0.1349620134
        H         0.4206825952        -2.0904911091        -0.5813063200
        H         0.2336940994        -1.7327827607         1.1451224868
        H         1.8319561105        -0.0400495074         1.0059075859
        H         2.0572928094        -0.3552168326        -0.7244347574
        H         0.8794533420         2.0272200817         0.2074903813
        H         0.4649311527         1.2962567345        -1.3609580820
        H        -0.9103522794         0.9566741802         1.1989666603
        H        -1.3708886567        -0.6509994218        -1.2022186570
        H        -1.9455734484        -0.9672922691         0.4519921871
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
