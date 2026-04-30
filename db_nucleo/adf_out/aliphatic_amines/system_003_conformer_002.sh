#!/bin/sh

AMS_JOBNAME="system_003_conformer_002" $AMSBIN/ams << eor
Task SinglePoint
System
    Atoms
        C         2.4982188956         0.6700884555        -0.5974441093
        C         1.5952290316        -0.5288122944        -0.8085664994
        O         0.3727403080        -0.4103994641        -0.0000107480
        C        -0.6508490290         0.2659754282        -0.5623964010
        O        -0.6251126275         0.7580882388        -1.6880427818
        C        -1.8736639084         0.3608750243         0.3489472224
        N        -1.8271508953        -0.2418473737         1.6783416052
        H         2.7576521550         0.7836946530         0.4642592545
        H         2.0186758042         1.5926727109        -0.9507207703
        H         3.4284820557         0.5257665418        -1.1657542694
        H         2.0579446260        -1.4561483841        -0.4512019631
        H         1.3034801255        -0.6426075078        -1.8598487210
        H        -2.7088124890        -0.0720885265        -0.2234199605
        H        -2.0974548113         1.4353090627         0.4386838595
        H        -1.6106699929        -1.2392583392         1.5915221348
        H        -1.0430160166         0.1560828390         2.2038945841
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
