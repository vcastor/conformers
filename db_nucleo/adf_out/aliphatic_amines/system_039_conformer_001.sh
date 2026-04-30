#!/bin/sh

AMS_JOBNAME="system_039_conformer_001" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        C         1.8459834179         0.2095013147        -0.0324043405
        C         0.6438988332        -0.1431745653        -0.5043347911
        C        -0.5362237259        -0.5065260725         0.3560260721
        N        -1.7209808146         0.3641030744         0.1697909238
        H         2.6690647091         0.4798207217        -0.6979586121
        H         2.0436819747         0.2373401516         1.0439576223
        H         0.4694732610        -0.1570793879        -1.5881892638
        H        -0.8511957205        -1.5409087750         0.1406045722
        H        -0.2432146929        -0.4729671673         1.4172218159
        H        -2.0271847061         0.2995114247        -0.8075168359
        H        -1.4247897485         1.3399224717         0.2857618015
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
