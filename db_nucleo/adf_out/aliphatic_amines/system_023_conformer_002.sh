#!/bin/sh

AMS_JOBNAME="system_023_conformer_002" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        N         2.5658898014         1.1360780359         0.1920640462
        C         1.9527301685        -0.1990516592         0.1036646392
        C         0.4413807707        -0.1571172508         0.0028590574
        C        -0.2843502291        -1.3549562027         0.1218078194
        C        -1.6767314519        -1.3629991935         0.0180178274
        C        -2.3726954407        -0.1660701706        -0.1973788632
        C        -1.6608867023         1.0314251061        -0.3086603737
        C        -0.2633146875         1.0351562309        -0.2110938010
        H         3.5806992920         1.0165970278         0.2633791689
        H         2.2872698236         1.5713385618         1.0783532020
        H         2.3500244568        -0.6889037779        -0.8017710836
        H         2.2189483218        -0.8613724204         0.9498644364
        H         0.2521570318        -2.2916804606         0.2990731278
        H        -2.2227894783        -2.3045801824         0.1108110954
        H        -3.4622332555        -0.1692822834        -0.2730657151
        H        -2.1939470945         1.9712368521        -0.4710714246
        H         0.2883077920         1.9724132555        -0.3039847362
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
