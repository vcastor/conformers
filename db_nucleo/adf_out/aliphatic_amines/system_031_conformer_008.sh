#!/bin/sh

AMS_JOBNAME="system_031_conformer_008" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        C        -1.6314908884        -0.7494018427        -0.3628293716
        C        -0.2630785335        -0.0849236581        -0.4352506938
        O        -0.3065943960         1.2738448346         0.0863887607
        C         0.7814584048        -0.8173670023         0.3923593608
        N         2.1140171293        -0.2121884853         0.2051803995
        H        -2.3719593212        -0.1761797606        -0.9395238360
        H        -1.9769506525        -0.8165517635         0.6796078832
        H        -1.5885009127        -1.7646809861        -0.7850686850
        H         0.0819306534        -0.0478868098        -1.4846094742
        H        -0.8919086617         1.7869601833        -0.5026516318
        H         0.4435917589        -0.8184428180         1.4476809934
        H         0.8185440751        -1.8648550644         0.0577270995
        H         2.7713135942        -0.6558485688         0.8541448339
        H         2.0571398182         0.7648971477         0.5125257746
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
