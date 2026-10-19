#!/bin/sh

AMS_JOBNAME="system_002_conformer_001" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        C         2.4299933366        -0.0720552773        -0.0639192482
        C         1.5815940387        -1.3475825708         0.1559208217
        N         0.2584973980        -0.8653366957        -0.2808618627
        C        -0.9928395494        -1.4427196161         0.2077880331
        C        -2.0678419806        -0.4317421540        -0.1948325301
        S        -1.2959243907         1.2323188877         0.0599780231
        C         0.3112800666         0.5164903086        -0.0642504991
        N         1.4727389696         1.0659552706         0.0658084747
        H         2.8693019519        -0.0599091940        -1.0764371431
        H         3.2475726557         0.0239044046         0.6617829722
        H         1.9177295734        -2.2067545591        -0.4372226422
        H         1.5447943830        -1.6328731433         1.2245670121
        H        -0.9615282462        -1.5719798776         1.3070560878
        H        -1.1819767589        -2.4190178281        -0.2587477989
        H        -2.9659631737        -0.4999787480         0.4275893963
        H        -2.3386607453        -0.5290693854        -1.2533728271
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
