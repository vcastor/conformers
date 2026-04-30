#!/bin/sh

AMS_JOBNAME="system_043_conformer_003" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        C         2.1311082274         0.0736980622        -0.3088951051
        C         1.1856514890        -0.7894306253         0.5371380628
        N        -0.1676622781        -0.2481854065         0.7633093233
        C        -0.9711193071        -0.1175889770        -0.4643481186
        C        -2.3428468197         0.4687251799        -0.1512314026
        H         3.1236768845        -0.3985668217        -0.3717622301
        H         2.2596292266         1.0696560599         0.1444850352
        H         1.7604397273         0.2103345735        -1.3351179320
        H         1.6411217806        -0.9595791650         1.5260787595
        H         1.0679416528        -1.7823686555         0.0710675848
        H        -0.0681782574         0.6877177216         1.1751449794
        H        -1.0797875475        -1.1273834229        -0.8954421666
        H        -0.4783606573         0.5055159095        -1.2370781287
        H        -2.9517401904         0.5396661309        -1.0641096788
        H        -2.8801940617        -0.1538374067         0.5799653648
        H        -2.2473825268         1.4832999840         0.2677345456
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
