#!/bin/sh

AMS_JOBNAME="system_015_conformer_002" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        C         1.2880527403         0.8256701947        -0.1126097128
        C        -0.0316252815         1.4771268093         0.3242052013
        C        -1.2255650477         0.6582583447        -0.1688282884
        N        -1.1284029483        -0.7251960999         0.3346506352
        C         0.0834725500        -1.3864683334        -0.1868886343
        C         1.3309385380        -0.6508047503         0.3055235747
        H         2.1476528709         1.3725521065         0.3048646267
        H         1.3720824899         0.8887599606        -1.2123414570
        H        -0.1049080209         2.5051552858        -0.0633769958
        H        -0.0696229893         1.5360890866         1.4254741607
        H        -1.2433483758         0.6853862509        -1.2807087295
        H        -2.1707661076         1.0946116229         0.1875303947
        H        -1.9460565101        -1.2455905151         0.0038664271
        H         0.0865278833        -2.4317002488         0.1569581274
        H         0.0917344338        -1.4007636036        -1.2989664520
        H         1.3765195718        -0.7236561467         1.4057282560
        H         2.2312362289        -1.1427136654        -0.0942841718
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
