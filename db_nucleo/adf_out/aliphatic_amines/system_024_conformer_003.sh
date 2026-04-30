#!/bin/sh

AMS_JOBNAME="system_024_conformer_003" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        O        -2.2618106360        -0.5307328651        -1.3267325646
        C        -2.1135544160        -0.0704750625         0.0384354024
        C        -1.1220718398         1.0853719488         0.0342486334
        N         0.2320435842         0.7522311961        -0.4345629046
        C         0.9359681453        -0.2347654715         0.4029336070
        C         2.4107734895        -0.2166351199         0.0156624063
        O         2.8979261993         1.1436397826         0.0224354255
        H        -2.8020329116        -1.3425435894        -1.2975421814
        H        -3.0819167662         0.2784092628         0.4368968004
        H        -1.7551957389        -0.8944163992         0.6777502091
        H        -1.0502016352         1.4886906951         1.0564088580
        H        -1.5158975182         1.8879950644        -0.6091272159
        H         0.1505570259         0.3726986252        -1.3845007477
        H         0.5425280953        -1.2643253544         0.3171841430
        H         0.8257610325         0.0826213216         1.4523130448
        H         3.0097030199        -0.7986220799         0.7291872287
        H         2.5423624648        -0.6575006987        -0.9902341135
        H         2.0943305339         1.6435268303        -0.2729566566
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
