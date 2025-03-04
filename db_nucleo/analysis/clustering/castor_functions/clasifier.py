# -*- coding: UTF-8 -*-
import pandas as pd

def reactivity_classifier(df, exp_par, spliter):
    """
    exp_par :: 'experimental_N' or 'experimental_Sn'
    spliter :: [non-reactive/reactive] or [non-reactive/bad/good/very good]
    """
    # Ensure the category is None in every call
    df['category'] = None

    # Assign categories
    df.loc[(df['source'] == 'non_reactive') & (df['category'].isnull()), 'category'] = 'No Reactive'
    df.loc[(df['source'] == 'peculiar') & (df['category'].isnull()), 'category'] = 'Peculiar'

    # Quantiles for the spliter only for the reactive ones and not peculiar
    mask_for_quantiles = ((df['source'] != 'peculiar') & (df['source'] != 'non_reactive'))
    q1 = df.loc[mask_for_quantiles, exp_par].quantile(0.25)
    q2 = df.loc[mask_for_quantiles, exp_par].quantile(0.75)

    q3 = df.loc[mask_for_quantiles, exp_par].quantile(0.50) # axuiliar

    # Encode categories
    cat_to_num = {
        'No Reactive': 0,
    }

    # For the remaining (reactive ones):
    remaining_mask = df['category'].isnull()

    if spliter == 2:
        df.loc[(remaining_mask) & (df[exp_par] > 0), 'category'] = 'Nucleophile'
        cat_to_num.update({'Nucleophile': 1})

    elif spliter == 3:
        df.loc[(remaining_mask) & (df[exp_par] > 0) & (df[exp_par] <= q3), 'category'] = 'Bad Nucleophile'
        df.loc[(remaining_mask) & (df[exp_par] > q3), 'category'] = 'Good Nucleophile'

        cat_to_num = {
            'Bad Nucleophile': 0,
            'Good Nucleophile': 1,
        }

    elif spliter == 4:
        df.loc[(remaining_mask) & (df[exp_par] > 0) & (df[exp_par] <= q1), 'category'] = 'Bad Nucleophile'
        df.loc[(remaining_mask) & (df[exp_par] > q1) & (df[exp_par] <= q2), 'category'] = 'Good Nucleophile'
        df.loc[(remaining_mask) & (df[exp_par] > q2), 'category'] = 'Very Good Nucleophile'

        cat_to_num.update({
            'Bad Nucleophile': 1,
            'Good Nucleophile': 2,
            'Very Good Nucleophile': 3
        })

    else:
        raise ValueError('Invalid spliter value')

    df['category'] = df['category'].map(cat_to_num)

    return df

