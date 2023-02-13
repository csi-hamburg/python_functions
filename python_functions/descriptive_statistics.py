# AUTOGENERATED! DO NOT EDIT! File to edit: ../00_descriptive_statistics.ipynb.

# %% auto 0
__all__ = ['stats_1group', 'finalize_stats_1group', 'stats_2groups', 'finalize_stats_2groups']

# %% ../00_descriptive_statistics.ipynb 3
def stats_1group(
    df, # df: dataframe with statistics; make sure that categorical columns are of type "object"
    columns, # # columns: columns to describe
    ):

    import pandas as pd

    df_describe = df.describe()

    target_df=pd.DataFrame(columns=columns)

    for col in columns:
        
        if df[col].dtypes == "object":
            
            target_df.loc[f"datatype",col] = "categorical"

            #target_df.loc["count",col]=df_describe[col]["count"]

            values = sorted(df[col].unique(), reverse=True)

            values = [x for x in values if not pd.isnull(x)]

            target_df.loc[f"values",col] = values

            n_1 = df[df[col] == values[0]].shape[0]

            n_2 = df[df[col] == values[1]].shape[0]

            target_df.loc[f"percent",col]= round(n_1 / (n_1 + n_2), 4)

        else:

            target_df.loc[f"datatype",col] = "continuous"

            target_df.loc["count",col]=df_describe[col]["count"]

            target_df.loc["mean",col]=round(df_describe[col]["mean"], 2)

            target_df.loc["std",col]=round(df_describe[col]["std"], 2)

            target_df.loc["median",col]=round(df_describe[col]["50%"], 2)

            target_df.loc["IQR25",col]=round(df_describe[col]["25%"], 2)

            target_df.loc["IQR75",col]=round(df_describe[col]["75%"], 2)

    return target_df

# %% ../00_descriptive_statistics.ipynb 4
def finalize_stats_1group(
    stats, # dataframe output by stats_2groups
    statistic="mean_std", # statistic to display ("mean_std","median_iqr")
    ):
    "Takes dataframe and extracts relevant indices for descriptive statistics table"

    import pandas as pd

    columns = [r"Metricᵃ", "Group"]

    pretty_df = pd.DataFrame(index=stats.columns, columns=columns)

    for idx, stats_column in enumerate(stats.columns):

        metric_name = stats_column.replace("_"," ").title()

        pretty_df.loc[stats_column, "Metricᵃ"] = metric_name

        if stats.loc["datatype",stats_column] == "categorical":

            string = f"{stats.loc['percent',stats_column]:.2%}"
            pretty_df.loc[stats_column, "Group"] = string

        if stats.loc["datatype",stats_column] == "continuous":

            if statistic == "mean_std":

                string = f"{stats.loc['mean',stats_column]:.2f} ± {stats.loc['std',stats_column]:.2f} ({int(stats.loc['count',stats_column])})"
            
            if statistic == "median_iqr":

                string = f"{stats.loc['median',stats_column]:.2f} ({int(stats.loc['IQR75',stats_column])-int(stats.loc['IQR25',stats_column])})"
        
        pretty_df.loc[stats_column, "Group"] = string
        
    return pretty_df

# %% ../00_descriptive_statistics.ipynb 5
def stats_2groups(df,columns,stats,group_col,covar=None):

# df: dataframe with statistics; make sure that categorical columns are of type "object"

# columns: columns to describe

# stats: statistical tests to apply to respective columns (length has to match)

# group_col: columns that differentiates groups

# covar: covariates for ancova

    import pandas as pd

    from scipy.stats import ttest_ind,chi2_contingency,mannwhitneyu

    from statsmodels.stats.multitest import multipletests

    from pingouin import ttest,mwu,compute_effsize

    import pingouin as pg


    values_group = df[group_col].unique()

    values_group = [int(x) for x in values_group if not pd.isnull(x)]



    data_controls=df[df[group_col]==0]

    data_patients=df[df[group_col]==1]


    df_control_describe = data_controls.describe()

    df_pat_describe = data_patients.describe()

    target_df=pd.DataFrame(columns=columns)

    for idx,col in enumerate(columns):


        stat = stats[idx]



        if df[col].dtypes == "object":

            target_df.loc[f"datatype",col] = "categorical"

            values = sorted(df[col].unique(), reverse=True)

            values = [x for x in values if not pd.isnull(x)]

            target_df.loc[f"values",col] = values

            n_contr_1 = data_controls[data_controls[col] == values[0]].shape[0]

            n_contr_2 = data_controls[data_controls[col] == values[1]].shape[0]

            target_df.loc[f"contr_percent",col]= n_contr_1 / (n_contr_1 + n_contr_2)

            n_pat_1 = data_patients[data_patients[col] == values[0]].shape[0]

            n_pat_2 = data_patients[data_patients[col] == values[1]].shape[0]

            target_df.loc[f"pat_percent",col]= n_pat_1 / (n_pat_1 + n_pat_2)

            statistic, p_val, _, _ = chi2_contingency(pd.crosstab(df[group_col],df[col]).T)


        else:

            target_df.loc[f"datatype",col] = "continuous"

            target_df.loc["pat_mean",col]=df_pat_describe[col]["mean"]

            target_df.loc["pat_std",col]=df_pat_describe[col]["std"]

            target_df.loc["pat_count",col]=df_pat_describe[col]["count"]

            target_df.loc["pat_median",col]=df_pat_describe[col]["50%"]

            target_df.loc["pat_IQR25",col]=df_pat_describe[col]["25%"]

            target_df.loc["pat_IQR75",col]=df_pat_describe[col]["75%"]

            target_df.loc["",col]="---"

            target_df.loc["contr_mean",col]=df_control_describe[col]["mean"]

            target_df.loc["contr_std",col]=df_control_describe[col]["std"]

            target_df.loc["contr_count",col]=df_control_describe[col]["count"]

            target_df.loc["contr_median",col]=df_control_describe[col]["50%"]

            target_df.loc["contr_IQR25",col]=df_control_describe[col]["25%"]

            target_df.loc["contr_IQR75",col]=df_control_describe[col]["75%"]
            


            if stat == "ttest": 
                stat_df = ttest(data_controls[col], data_patients[col])
                p_val, statistic = float(stat_df.loc["T-test","p-val"]), float(stat_df.loc["T-test","T"])
                cohen = compute_effsize(data_controls[col], data_patients[col], eftype="cohen")

            if stat == "mwu": 

                stat_df = mwu(x=data_controls[col],y=data_patients[col])
                p_val, statistic = float(stat_df.loc["MWU","p-val"]), float(stat_df.loc["MWU","RBC"])
                cohen = compute_effsize(data_controls[col], data_patients[col], eftype="cohen")

            if stat == "ancova": 
            
                stat_df = pg.ancova(df, dv=col, between=group_col, covar=covar)
                p_val, statistic = float(stat_df.loc[0,"p-unc"]), float(stat_df.loc[0,"F"])
                cohen = compute_effsize(data_controls[col], data_patients[col], eftype="cohen")
                target_df.loc["covariates",col]=covar
                target_df.loc["main_effect",col]=group_col

        target_df.loc[" ",col]="---"

        target_df.loc["stat",col]=statistic

        if cohen: target_df.loc["cohens_d",col] = cohen
        cohen = None

        target_df.loc["pval",col]=p_val

        target_df.loc['p_bonferroni',col] = target_df.loc['pval',col] * len(columns)

        target_df.loc["p_fdr"] = multipletests(target_df.loc["pval"], alpha=0.05, method="fdr_bh")[1]

        target_df.loc['p_bonferroni'][target_df.loc['p_bonferroni']>1] = 1



    print("n (total) controls: ", data_controls.shape[0])

    print("n (total) patients: ", data_patients.shape[0])



    return target_df

# %% ../00_descriptive_statistics.ipynb 6
def finalize_stats_2groups(stats):
    
    # stats: dataframe output by stats_2groups

    import pandas as pd

    columns = [r"Metricᵃ", "Patients", "Controls", r"p", r"pFDR", "Statᵇ"]

    pretty_df = pd.DataFrame(index=stats.columns, columns=columns)

    for idx, stats_column in enumerate(stats.columns):
        metric_name = stats_column.replace("_"," ").title()
        pretty_df.loc[stats_column, "Metricᵃ"] = metric_name

        if stats.loc["datatype",stats_column] == "continuous":

            pat_string = f"{stats.loc['pat_mean',stats_column]:.2f} ± {stats.loc['pat_std',stats_column]:.2f} ({int(stats.loc['pat_count',stats_column])})"
            pretty_df.loc[stats_column, "Patients"] = pat_string

            contr_string = f"{stats.loc['contr_mean',stats_column]:.2f} ± {stats.loc['contr_std',stats_column]:.2f} ({int(stats.loc['contr_count',stats_column])})"
            pretty_df.loc[stats_column, "Controls"] = contr_string

            pretty_df.loc[stats_column, "Statᵇ"] = f"{stats.loc['cohens_d',stats_column]:.2f}"
        
        elif stats.loc["datatype",stats_column] == "categorical":

            pat_string = f"{stats.loc['pat_percent',stats_column]:.2%}"
            pretty_df.loc[stats_column, "Patients"] = pat_string

            contr_string = f"{stats.loc['contr_percent',stats_column]:.2%}"
            pretty_df.loc[stats_column, "Controls"] = contr_string

            pretty_df.loc[stats_column, "Statᵇ"] = f"{stats.loc['stat',stats_column]:.2f}"

        if stats.loc['pval',stats_column] > 0.99:
            pretty_df.loc[stats_column, "p"] = ">0.99"
        elif stats.loc['pval',stats_column] < 0.001:
            pretty_df.loc[stats_column, "p"] = "<0.001"
        else:
            pretty_df.loc[stats_column, "p"] = f"{stats.loc['pval',stats_column]:.3f}"

        if stats.loc['p_fdr',stats_column] > 0.99:
            pretty_df.loc[stats_column, "pFDR"] = ">0.99"
        elif stats.loc['p_fdr',stats_column] < 0.001:
            pretty_df.loc[stats_column, "pFDR"] = "<0.001**"
        elif stats.loc['p_fdr',stats_column] < 0.05:
            pretty_df.loc[stats_column, "pFDR"] = f"{stats.loc['p_fdr',stats_column]:.3f}*"
        else:
            pretty_df.loc[stats_column, "pFDR"] = f"{stats.loc['p_fdr',stats_column]:.3f}"


        



    return pretty_df
