#!/bin/sh

AMS_JOBNAME="system_052_conformer_001" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        C         1.2507643509        -0.5065161758         0.3326275980
        N         0.0602464345        -0.0266579086        -0.3740010275
        C        -1.0997744289        -0.8495339777        -0.0211942937
        C        -0.1955226001         1.3758674843        -0.0348539904
        H         2.1227731632         0.0992863233         0.0481154625
        H         1.4479855455        -1.5532989311         0.0609536431
        H         1.1339077776        -0.4505044903         1.4380341775
        H        -1.9855379226        -0.5004857208        -0.5705795404
        H        -0.9098420844        -1.8975421297        -0.2934634206
        H        -1.3274464353        -0.8089574670         1.0674922482
        H        -1.0764320494         1.7370913591        -0.5841142888
        H        -0.3821361016         1.5174367723         1.0530889466
        H         0.6701758084         1.9912778354        -0.3180085616
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
