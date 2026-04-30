#!/bin/sh

AMS_JOBNAME="system_005_conformer_001" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        N         2.3381527835        -0.2023316934         0.0999858113
        C         0.9436611944        -0.0839681784         0.0711581160
        C         0.1284147682        -1.2235734430        -0.0819837001
        C        -1.2578088403        -1.0947987452        -0.1824969313
        C        -1.8662811397         0.1658720395        -0.1329882591
        C        -1.0596748761         1.3001091217         0.0243702894
        C         0.3275150418         1.1825676045         0.1254305551
        H         2.6688019428        -1.1045710142         0.4418732353
        H         2.8082683162         0.5578268477         0.5911586809
        H         0.5932300928        -2.2124609284        -0.1223126325
        H        -1.8691983877        -1.9928979382        -0.2992355754
        H        -2.9501996074         0.2628000162        -0.2148348009
        H        -1.5147805203         2.2924833755         0.0706641772
        H         0.9478631105         2.0747131337         0.2464946339
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
