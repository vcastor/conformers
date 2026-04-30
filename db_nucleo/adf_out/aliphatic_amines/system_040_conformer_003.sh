#!/bin/sh

AMS_JOBNAME="system_040_conformer_003" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        C         1.9338250980         0.4666981246        -0.2232634235
        C         0.6550298856        -0.3351261003        -0.4724904765
        C        -0.5056313904         0.1307315974         0.4030571851
        N        -1.7119898679        -0.6908504177         0.1682455938
        H         1.7771031222         1.5376973148        -0.4263840981
        H         2.2626142333         0.3688532949         0.8232398526
        H         2.7552398357         0.1201190252        -0.8668264640
        H         0.3608996637        -0.2460018281        -1.5331448068
        H         0.8346651775        -1.4068866026        -0.2849670519
        H        -0.2275469649         0.0252173747         1.4648368650
        H        -0.6788455667         1.2107004014         0.2246017440
        H        -2.4747470758        -0.3329394920         0.7525301190
        H        -2.0295263940        -0.5322182942        -0.7948425980
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
