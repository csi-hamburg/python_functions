python_functions
================

<!-- WARNING: THIS FILE WAS AUTOGENERATED! DO NOT EDIT! -->

## Install

``` sh
git clone https://github.com/csi-hamburg/python_functions
cd python_functions
python setup.py install
```

## How to use

stats = stats_2groups(statistics_df,list(variables), (\[“ttest”\] \*
12 + \[“ancova”\] \* 8), ‘diagnosis_metabolic_syndrome’, \[‘base_age’,
‘base_sex_numeric’, ‘base_education_isced’\])

stats_prettified = finalize_stats_2groups(stats)
