1. pip R

2. pip install sklearn
               statsmodels
               rpy2==2.9.4
               matplotlib
               seaborn

3. set env
   export ONLINE_ANALYSIS_LOG = /Users/majing/workpro/superset/incubator-superset/online-logs/

   export R_PATH=
4. install R packages
   system("locate libSM.6.dylib")
   install.packages("dplyr",lib=.libPaths()[2])
   lme4, reshape2, ggplot2, dplyr, sampling, ROCR

