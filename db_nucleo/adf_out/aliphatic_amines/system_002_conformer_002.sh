#!/bin/sh

AMS_JOBNAME="system_002_conformer_002" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        C         1.6432039354         0.3829101505        -0.3412642249
        C         0.3168951367        -0.1461687494        -0.8916579258
        C        -0.8973419952         0.2003214511        -0.0187733633
        N        -0.9176483026        -0.3904762584         1.3363681554
        H         2.4796853156         0.1354376936        -1.0107561441
        H         1.6136249702         1.4784860456        -0.2295772758
        H         1.8757244081        -0.0489099653         0.6445396530
        H         0.3698069823        -1.2426930189        -1.0100182692
        H         0.1440791443         0.2679941417        -1.8996892492
        H        -1.8167356128        -0.1185141760        -0.5343778702
        H        -0.9632031205         1.2954753261         0.0953562329
        H        -0.8170934412        -1.4085823776         1.2501534861
        H        -0.0785226441        -0.0894713000         1.8436328791
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
