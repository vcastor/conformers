#!/bin/sh

AMS_JOBNAME="system_031_conformer_005" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        C        -1.6009434112        -0.7612268974        -0.3467348778
        C        -0.2396649400        -0.0781003778        -0.3329146744
        O        -0.3157341745         1.2358535538         0.2845587244
        C         0.7954406637        -0.8654361694         0.4691026658
        N         2.1552779341        -0.3002274872         0.4825802445
        H        -1.9760051957        -0.8930874121         0.6796309205
        H        -2.3336319629        -0.1655697592        -0.9110435896
        H        -1.5315485089        -1.7499414741        -0.8248561743
        H         0.1303409400         0.0379381488        -1.3695437190
        H        -0.9187695735         1.7735997823        -0.2634569487
        H         0.8420624129        -1.8892414237         0.0691919592
        H         0.4388008543        -0.9392715281         1.5106011341
        H         2.0841854942         0.6853654324         0.7596131930
        H         2.5077015353        -0.2732789822        -0.4810474444
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
