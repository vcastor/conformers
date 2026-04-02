# -*- coding: UTF-8 -*-
import pandas as pd

def family_classifier(df, family):
    # Every loop restart the category column
    df['category'] = 0

    # Assign categories
    if family == 'aliphatic_amines':
        df.loc[df['family'] == 'aliphatic_amines', 'category'] = 1
    elif family == 'pyridines_quinolines_etc':
        df.loc[df['family'] == 'pyridines_quinolines_etc', 'category'] = 1
    elif family == 'azoles_and_azole_anions':
        df.loc[df['family'] == 'azoles_and_azole_anions', 'category'] = 1

    return df

