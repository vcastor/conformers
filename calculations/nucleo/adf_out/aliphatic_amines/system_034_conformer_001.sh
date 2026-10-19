#!/bin/sh

AMS_JOBNAME="system_034_conformer_001" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        N        -2.1341060185        -0.4920006602        -0.0073893885
        C        -0.7752695974        -1.0111817505        -0.0811151506
        C         0.3387335785         0.0308745027        -0.0036551940
        F         0.2700421608         0.9549880961        -1.0228640741
        F         0.3058502557         0.7467275068         1.1729902364
        F         1.5815745066        -0.5559139348        -0.0809004694
        H        -2.2690743983         0.0291165468         0.8635085243
        H        -2.3057491022         0.1663476640        -0.7724732695
        H        -0.5990101203        -1.7178685857         0.7419689842
        H        -0.6330843724        -1.5559709236        -1.0250047205
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
