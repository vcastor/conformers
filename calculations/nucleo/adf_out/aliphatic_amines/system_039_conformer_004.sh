#!/bin/sh

AMS_JOBNAME="system_039_conformer_004" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        C         1.9449085249         0.2171421725        -0.0448552799
        C         0.7230800051        -0.0508296293        -0.5169177828
        C        -0.4737280015        -0.3596831008         0.3349463151
        N        -1.5741452326         0.6018920120         0.0644652756
        H         2.7845372345         0.4181103428        -0.7138485326
        H         2.1440971498         0.2379828668         1.0309085753
        H         0.5541159275        -0.0629714429        -1.6016664425
        H        -0.2009665896        -0.2831087467         1.3983943324
        H        -0.7793831994        -1.4085071681         0.1480182677
        H        -1.8576693826         0.4968861771        -0.9166800903
        H        -2.3963336487         0.3026297075         0.6001943263
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
