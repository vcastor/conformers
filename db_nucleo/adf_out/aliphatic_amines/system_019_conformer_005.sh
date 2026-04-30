#!/bin/sh

AMS_JOBNAME="system_019_conformer_005" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        N         1.0771749283         1.2320718219         0.4352525162
        C         0.4632001469         0.3892487284        -0.6063284104
        C        -0.6399433112        -0.5364625145        -0.0896795475
        O        -1.2721512372        -1.2946860645        -1.1469613642
        H         1.4442364967         0.6290716899         1.1800005337
        H         0.3424170480         1.7892579194         0.8856034279
        H         0.0476421108         1.0424787395        -1.3890546289
        H         1.2561184361        -0.2155100995        -1.0761763296
        H        -0.2321227911        -1.2145823649         0.6813596865
        H        -1.4430870611         0.0574403676         0.3709550123
        H        -0.5885335139        -1.8809577859        -1.5256977588
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
