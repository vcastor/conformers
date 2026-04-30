#!/bin/sh

AMS_JOBNAME="system_010_conformer_001" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        C         2.2673004428         0.7191338660         0.9673852794
        N         1.6871917876        -0.2142320126         0.2737825166
        N         0.3498968657        -0.2362001927         0.1640414702
        C        -0.5095146258         0.9197267803         0.4777350106
        C        -1.8002385935         0.6528503702        -0.3194781856
        C        -1.7311806969        -0.8443159030        -0.6799226433
        C        -0.2369662365        -1.0729116516        -0.8906062009
        H         3.3532856806         0.6628720605         1.0512391754
        H         1.7338679980         1.5257273205         1.4845810920
        H        -0.0096884568         1.8560419119         0.1675350446
        H        -0.6807756400         0.9816099579         1.5649514261
        H        -1.7958801665         1.2562667887        -1.2386502926
        H        -2.7015276207         0.9141519935         0.2489368803
        H        -2.3243599660        -1.0968081055        -1.5676423329
        H        -2.0856458412        -1.4587138610         0.1614242385
        H         0.0803728323        -0.7281527465        -1.8936627460
        H         0.0803776412        -2.1159703110        -0.7616429324
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
