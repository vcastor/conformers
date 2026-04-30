#!/bin/sh

AMS_JOBNAME="system_006_conformer_002" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        C         1.8109681975         0.6282840078        -0.1213815170
        N         0.4151147202         0.6007995785        -0.5670907450
        N        -0.4198961814         0.1212538736         0.5187726358
        C        -1.8177381482         0.1076774405         0.0781305381
        H         1.9308785103         1.3905887058         0.6607477447
        H         2.1603136452        -0.3429497470         0.2815567582
        H         2.4457623800         0.8952105312        -0.9770972198
        H         0.3490096789        -0.0755756109        -1.3444141793
        H        -0.1482610587        -0.8533784875         0.7247372914
        H        -2.1592563286         1.1387384170        -0.0873000311
        H        -2.4289911268        -0.3462803101         0.8697327872
        H        -1.9755409957        -0.4669062554        -0.8560576541
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
