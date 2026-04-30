#!/bin/sh

AMS_JOBNAME="system_025_conformer_002" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        C         2.1673371164         0.3002819452         0.2071022301
        O         0.8393569268        -0.1649044495        -0.1778669851
        C        -0.1832303109         0.6078811357         0.2451572601
        O        -0.0366227203         1.6335101110         0.9065851887
        C        -1.5511224779         0.0819593763        -0.1804265989
        N        -1.6363936506        -1.1622784984        -0.9407023571
        H         2.3445136069         1.3043267103        -0.1964312082
        H         2.8624571513        -0.4222959682        -0.2286683922
        H         2.2548861741         0.3149952238         1.3000530686
        H        -2.1370549409        -0.0110121549         0.7470359415
        H        -2.0208444950         0.8973776540        -0.7524698266
        H        -1.0844533723        -1.0751875353        -1.7991581067
        H        -1.1901574666        -1.9160626566        -0.4097400412
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
