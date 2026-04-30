#!/bin/sh

AMS_JOBNAME="system_024_conformer_001" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        O        -2.6810920882        -0.1770141297        -1.1244365163
        C        -2.2050480289         0.5043928464         0.0631079929
        C        -0.7372049561         0.8151637594        -0.1387643899
        N         0.0554613295        -0.4211152951        -0.2295122847
        C         1.4350448062        -0.2031104222        -0.6948978845
        C         2.2940896368         0.2435823089         0.4883721425
        O         2.0595712583        -0.6392373424         1.6066709401
        H        -3.5870895082        -0.4844798953        -0.9337067895
        H        -2.3427698656        -0.1393385415         0.9484210494
        H        -2.7614702784         1.4436847476         0.2178926023
        H        -0.6212975168         1.4401717018        -1.0486763983
        H        -0.3898502221         1.4160136956         0.7158998160
        H        -0.4171367921        -1.0497813315        -0.8839110957
        H         1.5027581189         0.5444116719        -1.5097844745
        H         1.8141877825        -1.1624435257        -1.0764894709
        H         3.3605398335         0.2018746944         0.2274929378
        H         2.0508712112         1.2832915445         0.7747532469
        H         1.1097074080        -0.8908984008         1.4653679509
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
