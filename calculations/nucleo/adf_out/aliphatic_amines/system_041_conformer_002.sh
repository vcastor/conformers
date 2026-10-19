#!/bin/sh

AMS_JOBNAME="system_041_conformer_002" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        C         2.6378158269         0.0192021369         0.1185475677
        C         1.2447403604        -0.5834710170         0.3111550164
        C         0.1282846200         0.3243216904        -0.2097274321
        C        -1.2635714879        -0.2672688171        -0.0079385371
        N        -2.3045473782         0.6251908627        -0.5612425415
        H         2.7275417589         0.9806834398         0.6483440985
        H         2.8427330396         0.2061189307        -0.9474140868
        H         3.4237458925        -0.6492894591         0.5000988819
        H         1.0757728486        -0.7902930020         1.3820081953
        H         1.1884415642        -1.5580942746        -0.2038468020
        H         0.2811733106         0.5269608205        -1.2840496442
        H         0.1826650060         1.3015416942         0.3043737931
        H        -1.4107261865        -0.4831069881         1.0687806409
        H        -1.3315758384        -1.2322722652        -0.5368004721
        H        -2.3056244077         1.4964967980        -0.0186985522
        H        -3.2248283743         0.2100739429        -0.3818562943
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
