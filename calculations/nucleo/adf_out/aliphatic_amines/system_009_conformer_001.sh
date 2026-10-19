#!/bin/sh

AMS_JOBNAME="system_009_conformer_001" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        C         1.2703722416        -0.2485942950        -0.1908056098
        C        -0.0135636570         0.5660353494        -0.0215374406
        N        -1.2412205350        -0.2265257783         0.2060133849
        H         1.1915688036        -0.9287538309        -1.0533411558
        H         1.4705827701        -0.8558946936         0.7056792970
        H         2.1367379888         0.4114347197        -0.3556698819
        H        -0.1790206257         1.1880287304        -0.9155266505
        H         0.0961599899         1.2608199672         0.8260952173
        H        -1.0959365916        -0.8205927345         1.0306232347
        H        -1.3476616673        -0.8897223407        -0.5704372339
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
