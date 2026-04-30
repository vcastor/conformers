#!/bin/sh

AMS_JOBNAME="system_024_conformer_002" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        O        -2.2191742987         1.6490287737         0.7697982483
        C        -2.3341943930         0.4208890426         0.0080712420
        C        -1.0683666154         0.2640867611        -0.8075203177
        N         0.0995756850         0.0704609834         0.0633893249
        C         1.3748179172         0.1334272315        -0.6675507712
        C         2.4855779100        -0.3217047002         0.2712682537
        O         2.1441027576        -1.6045487126         0.8414406129
        H        -2.9774958289         1.6779383041         1.3831242870
        H        -3.2053206489         0.4660526696        -0.6667264898
        H        -2.4574017428        -0.4375985136         0.6902144147
        H        -1.1742278699        -0.6138311275        -1.4640749913
        H        -0.9545448429         1.1533303151        -1.4622934613
        H         0.0917301989         0.8265668683         0.7577854114
        H         1.3080942428        -0.5603160056        -1.5211360745
        H         1.6022338536         1.1408465269        -1.0680082989
        H         3.4365416118        -0.4282717263        -0.2685760191
        H         2.6263668464         0.4229290939         1.0777389999
        H         1.1609573458        -1.5341176982         0.9308550033
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
