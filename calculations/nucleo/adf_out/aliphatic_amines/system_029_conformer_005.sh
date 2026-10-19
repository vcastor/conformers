#!/bin/sh

AMS_JOBNAME="system_029_conformer_005" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        C        -2.3167994111         0.6004354301        -0.3804571995
        C        -1.3703807721        -0.5605175565        -0.0648559674
        C         0.0609112060        -0.3723695799        -0.5852483717
        N         0.8051019896        -1.6383454093        -0.4217274599
        C         0.7393597806         0.8265202903         0.0885180473
        O         2.0577742840         1.1041079780        -0.4335237003
        H        -2.3264177420         0.8158732225        -1.4601785907
        H        -2.0319706077         1.5241785930         0.1431761687
        H        -3.3445810467         0.3558552006        -0.0783945457
        H        -1.7604213773        -1.4885287528        -0.5108415566
        H        -1.3329672606        -0.7314530007         1.0258297194
        H         0.0173622768        -0.1681692516        -1.6695632887
        H         0.9396809327        -1.8244993693         0.5795677012
        H         1.7457882475        -1.5435389380        -0.8182389645
        H         0.1611508400         1.7434230906        -0.0879523860
        H         0.7891170738         0.6551236949         1.1798098746
        H         2.6465119542         0.3890518711        -0.1232400768
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
