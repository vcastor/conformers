#!/bin/sh

AMS_JOBNAME="system_043_conformer_002" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        C         2.3893227306        -0.0642871035        -0.1039562974
        C         0.9415174470         0.0167823813         0.3632121341
        N         0.0234933917        -0.4832959506        -0.6736275741
        C        -1.3715134720        -0.5944763576        -0.2074390947
        C        -2.0595215877         0.7637929803        -0.0922584019
        H         2.6752375787        -1.1060126245        -0.3197971602
        H         2.5411785839         0.5279485424        -1.0185311948
        H         3.0686682298         0.3161389370         0.6720672499
        H         0.8209669005        -0.5457115596         1.3144109730
        H         0.6818941263         1.0640328468         0.5824835810
        H         0.3377479910        -1.4272398377        -0.9225754738
        H        -1.9116900798        -1.2156282074        -0.9381974295
        H        -1.4317158848        -1.1194783830         0.7703156172
        H        -2.0094946628         1.3055675145        -1.0487169545
        H        -1.5961209709         1.3914163733         0.6825522843
        H        -3.1176729791         0.6321235892         0.1769966344
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
