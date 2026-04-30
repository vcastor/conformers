#!/bin/sh

AMS_JOBNAME="system_019_conformer_001" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        C        -2.1516021687        -1.5265789079        -0.4592260807
        N        -1.6114692413        -0.2017312474        -0.1750430554
        C        -2.5238400088         0.8645844901         0.2244053555
        C        -0.2614014536        -0.0279252783        -0.0462988955
        C         0.3070417362         1.2142828153         0.3424972458
        C         1.6875373383         1.3388653643         0.4308109385
        N         2.5751593324         0.3509419241         0.1786787318
        C         2.0254587639        -0.8321671514        -0.1751200396
        C         0.6635614665        -1.0764707045        -0.2961048493
        H        -1.9471407593        -2.2406212644         0.3574256713
        H        -1.7271137023        -1.9325242206        -1.3898236775
        H        -3.2353083538        -1.4462637059        -0.5881333235
        H        -2.3233679313         1.7868913431        -0.3415056740
        H        -2.4447854573         1.0926428257         1.3013912646
        H        -3.5499387169         0.5502401780         0.0098159691
        H        -0.3171509815         2.0760626400         0.5747451184
        H         2.1135228738         2.3030371626         0.7267912391
        H         2.7283788325        -1.6484126493        -0.3711329967
        H         0.3290413711        -2.0734019175        -0.5798877699
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
