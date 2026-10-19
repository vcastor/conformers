#!/bin/sh

AMS_JOBNAME="system_019_conformer_002" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        N         1.4676099088         0.6079105541        -0.0603825503
        C         0.3141960911         0.3348720716        -0.9375054177
        C        -0.7614562572        -0.5806655732        -0.3605556811
        O        -1.4432696567        -0.0047306579         0.7796293188
        H         1.1478680096         1.0855222766         0.7887668031
        H         1.8704420744        -0.2808280507         0.2573130181
        H        -0.1431758971         1.2987375626        -1.2101252251
        H         0.6844692769        -0.1234599162        -1.8688146445
        H        -0.3222084866        -1.5552659978        -0.0835087012
        H        -1.5412010958        -0.7581141986        -1.1154474139
        H        -0.8183227149        -0.0266076333         1.5299036310
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
