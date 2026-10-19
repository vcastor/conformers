#!/bin/sh

AMS_JOBNAME="system_010_conformer_001" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        N         1.9460305628         0.2934412860        -0.5405819621
        C         1.8803151196        -0.2464069771         0.7825166671
        C         0.6290320581        -1.1149345817         0.9981479531
        C        -0.6794501694        -0.3174905282         1.0032587835
        C        -1.1602036295         0.2571813722        -0.3175949720
        O        -0.3224318554         0.6136259619        -1.2272092682
        O        -2.4013968792         0.4067483752        -0.5126711491
        H         2.0584576134        -0.3377440757        -1.3291477807
        H         2.2369881979         1.2543580847        -0.6912871733
        H         1.9057691325         0.5826502011         1.5015541233
        H         2.7671847984        -0.8838512221         0.9707270876
        H         0.7422036984        -1.6163422156         1.9701859677
        H         0.5970008938        -1.9048000974         0.2315157184
        H        -1.4950770812        -0.9552690175         1.3779282291
        H        -0.5996182943         0.5269171411         1.7095196237
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
