#!/bin/sh

AMS_JOBNAME="system_041_conformer_004" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        C         2.0866485148         0.1680213490        -0.3910173829
        C         1.1229208654        -0.0990471259         0.7684823979
        C        -0.2086911459         0.6564481033         0.6575569166
        C        -1.0754505681         0.2733984083        -0.5510944154
        N        -1.5425392211        -1.1288140328        -0.5981376429
        H         2.2932980295         1.2455125882        -0.4896470292
        H         3.0463313007        -0.3461693936        -0.2355247015
        H         1.6792901945        -0.1800836092        -1.3522519481
        H         1.6080385318         0.1850899055         1.7162210168
        H         0.9305005519        -1.1832775372         0.8484714111
        H        -0.0050896004         1.7410630605         0.6054174415
        H        -0.7975936906         0.4933186621         1.5767986716
        H        -0.5288974431         0.4720820046        -1.4865813276
        H        -1.9653515285         0.9216474988        -0.5704685469
        H        -2.0246382638        -1.3413857339         0.2833782386
        H        -0.7267359726        -1.7510096546        -0.5998692680
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
