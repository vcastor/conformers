#!/bin/sh

AMS_JOBNAME="system_023_conformer_001" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        C         3.5317505496        -0.1796189891        -0.5069878978
        C         2.1001399631        -0.6400912988        -0.3421636281
        O         1.7574144200        -1.8301034655        -0.3834594741
        N         1.2110426821         0.3980096095        -0.1415085820
        C        -0.1719757817         0.3629754739         0.0497018307
        C        -0.8391118164         1.5839266569         0.2583515059
        C        -2.2150695905         1.5787466725         0.4520206909
        N        -2.9756020046         0.4624817439         0.4541382135
        C        -2.3189390736        -0.6970090192         0.2511739578
        C        -0.9443603474        -0.8107408846         0.0462240278
        H         3.8607772831         0.3802121316         0.3806502738
        H         4.1771357731        -1.0515980581        -0.6489970694
        H         3.6215243458         0.4891505353        -1.3758253488
        H         1.6224714289         1.3301662418        -0.1210071739
        H        -0.2872213506         2.5261150868         0.2695104725
        H        -2.7389802874         2.5248413812         0.6161311048
        H        -2.9306886792        -1.6038355481         0.2512425297
        H        -0.4814057035        -1.7806904405        -0.1116886035
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
