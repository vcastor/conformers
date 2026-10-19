#!/bin/sh

AMS_JOBNAME="system_059_conformer_002" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        F         1.7870481840         0.5435237013         0.9065149140
        C         1.0262549290         0.1554834410        -0.1758251895
        F         1.8745684803        -0.4860395018        -1.0450650675
        F         0.6188748929         1.3153712261        -0.7978351371
        C        -0.1318864639        -0.7418629870         0.2338341005
        C        -1.0596721963        -1.1071633232        -0.9616558887
        C        -2.3244376066        -0.2714843840        -0.7208348079
        C        -2.3921652907        -0.2323774889         0.8077488359
        N        -0.9835353738        -0.0994885266         1.2747596307
        H         0.3433226976        -1.6480291719         0.6408894310
        H        -1.2952599222        -2.1788334084        -0.9052085863
        H        -0.5870385758        -0.9218960927        -1.9343322607
        H        -2.1989048472         0.7467554511        -1.1191463862
        H        -3.2163344332        -0.7170263035        -1.1827933242
        H        -2.8093475564        -1.1767480625         1.1948110089
        H        -2.9927448063         0.5935424840         1.2099266357
        H        -0.7664045511         0.9010034756         1.3061384769
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
