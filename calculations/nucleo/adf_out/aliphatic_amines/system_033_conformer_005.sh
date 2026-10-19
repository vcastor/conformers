#!/bin/sh

AMS_JOBNAME="system_033_conformer_005" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        N         1.0772790640         1.2314688679         0.4340171332
        C         0.4625183918         0.3884188785        -0.6064609982
        C        -0.6409040107        -0.5374732096        -0.0899835618
        O        -1.2729451190        -1.2961112126        -1.1461358804
        H         1.4457167287         0.6297671550         1.1790087419
        H         0.3441106089         1.7906492130         0.8842867547
        H         0.0470374428         1.0412245708        -1.3895664268
        H         1.2554364570        -0.2161736764        -1.0767139782
        H        -0.2333960367        -1.2145156769         0.6824331813
        H        -1.4442217936         0.0566490730         0.3702575528
        H        -0.5900136909        -1.8830076799        -1.5247956920
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
