#!/bin/sh

AMS_JOBNAME="system_032_conformer_003" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        O        -2.2606111433        -0.5008582372        -1.3500896555
        C        -2.1145979686        -0.0750248510         0.0252183849
        C        -1.1219761019         1.0798855203         0.0496187741
        N         0.2315780166         0.7557161290        -0.4245853806
        C         0.9339089969        -0.2510920929         0.3897728125
        C         2.4124792438        -0.2127665988         0.0163210263
        O         2.8870413758         1.1495421237         0.0597329735
        H        -2.7823079657        -1.3251205498        -1.3428539082
        H        -3.0832092860         0.2642772578         0.4318556557
        H        -1.7568098758        -0.9137146299         0.6454606885
        H        -1.0514258245         1.4611435662         1.0800694136
        H        -1.5144961878         1.8962896427        -0.5769172712
        H         0.1503918343         0.4001266483        -1.3835742366
        H         0.5467077023        -1.2797762594         0.2719745362
        H         0.8138287106         0.0358872632         1.4466412639
        H         3.0094035603        -0.8070587312         0.7214319948
        H         2.5562308373        -0.6298437905        -0.9981344914
        H         2.0808075427         1.6489253634        -0.2294066413
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
