#!/bin/sh

AMS_JOBNAME="system_031_conformer_002" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        C        -1.5295605086        -0.6181888010        -0.3823676214
        C        -0.1363229313        -0.2396247139        -0.8821769111
        O        -0.0122583762         1.1974192093        -1.0102037950
        C         0.9833779764        -0.7302811323         0.0510507759
        N         1.0031457981         0.1259961501         1.2548887042
        H        -1.6464757416        -1.7124070530        -0.3560426325
        H        -2.2991136373        -0.2023435249        -1.0475775283
        H        -1.7070639787        -0.2240229340         0.6305584265
        H         0.0235961960        -0.6658753659        -1.8847718996
        H         0.3259297110         1.4468202469        -0.1105823277
        H         0.8495261230        -1.8042249756         0.2680966863
        H         1.9487625744        -0.6063149323        -0.4602085569
        H         1.9133691779         0.0593790796         1.7150306394
        H         0.3205996848        -0.2089558468         1.9399874535
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
