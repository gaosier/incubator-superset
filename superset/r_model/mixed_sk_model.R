library(lme4)
library(reshape2)
library(ggplot2)
library(dplyr)
library(sampling)
library(ROCR)

#获取数据
get_data<-function(dirname, filename){
    setwd(dirname)
    data<-read.csv(filename, stringsAsFactors = FALSE)
    head(data)
    return (data)
}

# 分层抽样
stratified_sampling<-function(dirname, filename, sort_cols, unique_col){
    data<-get_data(dirname, filename)
    data_xh_or<-data[order(data[sort_cols])]
    ins_id_set<-unique(data_xh_or[unique_col])
}


