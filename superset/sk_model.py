# -*- coding:utf-8 -*-
# __author__ = majing

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import matplotlib
matplotlib.use('TkAgg')

import inspect
import logging
import uuid
import os
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import statsmodels.api as sm
import rpy2.robjects as robjects

from rpy2.robjects import r, pandas2ri
from flask import request
from numpy import shape
from pandas.core.frame import DataFrame
from sklearn.linear_model import LogisticRegressionCV
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.metrics import (confusion_matrix, precision_recall_curve, average_precision_score, roc_auc_score,
                             roc_curve, precision_score, recall_score)


from superset import app
from superset.exceptions import SupersetParamException
from superset.analysis_log import ana_code_logger, ana_image_logger, ana_param_logger

pandas2ri.activate()

os.environ['R_HOME'] = os.environ.get('R_PATH')

config = app.config
logger = logging.getLogger('analysis')

METRIC_KEYS = [
    'metric', 'metrics', 'percent_metrics', 'metric_2', 'secondary_metric',
    'x', 'y', 'size',
]

IMAGE_URL = config.get("IMG_UPLOAD_URL")
IMAGE_PATH= config.get("IMG_UPLOAD_FOLDER")

R_MODEL_FILE = config.get("R_MODEL_FILE_PATH")

BASE_QUERY = "SELECT * FROM  "


class BaseSkModel(object):
    """
    机器学习模型的基类
    """

    sk_type = None
    verbose_name = 'Base SK Model'

    def __init__(self, datasource, form_data):
        if not datasource:
            raise Exception("缺少数据源")
        self.datasource = datasource
        self.form_data = form_data

        self.query = BASE_QUERY + self.datasource.table_name + ';'

        # 跑模型所需的参数
        self.df = None
        self.model = None
        self.x_col = None
        self.y_col = None
        self.extra_factor = None       # 混合模型所需的参数

        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        self.validate_datasets = None

        self.get_dataset_cols()

    def get_dataset_cols(self):
        """
        获取测试集/训练集 验证集所选的列
        """
        model_params = self.form_data.get("model_param", {})
        self.x_col = model_params.get("dataset", {}).get("x_col")
        self.y_col = model_params.get("dataset", {}).get("y_col")
        print("self.x_col: ", self.x_col)

    def get_df(self, query_obj=None):
        """
         Returns a pandas dataframe based on the query object
        """
        self.error_msg = ''
        self.results = None

        self.results = self.datasource.query(query_obj, special_sql=self.query)
        self.query = self.results.query
        self.status = self.results.status
        self.error_message = self.results.error_message

        df = self.results.df
        if df is None or df.empty:
            return pd.DataFrame()
        else:
            df.replace([np.inf, -np.inf], np.nan)
        return df

    def get_column_fillna(self, df, fills):
        """
        获取每一列需要填充的值
        """
        fillna = {}
        for field, na in fills:
            if na == 'median':     # 中位数
                value = df[field].median()

            elif na == 'mode':    # 众数
                 mode = df[field].mode().tolist()
                 value = mode[0]

            elif na == 'mean':   # 平均值
                value = df[field].mean()

            else:
                value = na
            fillna[field] = value
        return fillna

    def deal_na(self, df):
        """
        缺失值处理
        """
        ana_code_logger.info(" =========== 缺失值处理 ===========")
        operate_info = self.form_data.get("null_operate", {})
        ana_code_logger.info("null_operate: %s" % operate_info)
        operate = operate_info.get("operate", None)

        detail = operate_info.get("detail", [])
        fillna = self.get_column_fillna(df, detail)

        if operate == "fill":
            df = df.fillna(fillna)
        else:
            df = df.dropna()
        print("df: ", df.head(5))
        ana_code_logger.info("============= 缺失值处理结束 =================")
        return df

    def deal_variable_box(self, df):
        """
        变量分箱处理
        """
        ana_code_logger.info(" =========== 变量分箱处理 ===========")

        variable_box = self.form_data.get("variable_box", [])
        ana_code_logger.info("variable_box: %s " % variable_box)
        for item in variable_box:
            field = item.get("field")
            bins = item.get("bins")
            labels = item.get("labels")
            if not field or (not bins) or (not labels):
                return df
            col = pd.cut(df[field], bins=bins, labels=labels)
            df[field] = col

        ana_code_logger.info(" =========== 变量分箱处理结束 ===========")
        return df

    def deal_dummy_variable(self, df):
        """
        哑变量处理
        """
        ana_code_logger.info("=========== 哑变量处理 ===========")

        dummy_variable = self.form_data.get("dummy_variable", {})
        deal_dummy_variable = {}
        for item in dummy_variable:
            deal_dummy_variable[item.get("name")] = item.get("val")

        for field, value in deal_dummy_variable.items():
            df[field] = df[field].map(value)

        ana_code_logger.info(" =========== 哑变量处理结束 ===========")
        return df

    def variable_describe(self, df):
        """
        变量分布
        """
        data = df.describe()
        return data.to_html()

    def correlation_analysis(self, df):
        """
        变量相关性分析
        """
        ana_code_logger.info("=========== 变量相关性分析 ===========")

        correlation_analysis = self.form_data.get("correlation_analysis", [])
        count = len(correlation_analysis)

        if count < 3:
            row = 1
        else:
            row = count//3 if count % 3 == 0 else count //3 + 1

        fig, ax = plt.subplots(row, 3, figsize=(7, 3))
        count = -1
        for field, func, chart in correlation_analysis:
            count += 1
            if func == 'matplotlib' and chart == 'pie':
                ln = df[field].value_counts()
                explode = [0]*ln
                explode[1] = 0.1
                df[field].value_counts().plot.pie(explode=explode, autopct='%1.1f%%', ax=ax[0], shadow=True)
                ax[count].set_title(field)
                ax[count].set_ylabel('y')
            elif func == 'seaborn' and chart == 'countplot':
                sns.countplot(field, data=df, ax=ax[count])
                ax[count].set_title(field)
                ax[count].set_ylabel('y')
            elif func == 'seaborn' and chart == 'heatmap' and field == 'all':
                sns.heatmap(df.corr(), annot=True, cmap='RdYlGn', linewidths=0.5)
                fig = plt.gcf()
                fig.set_size_inches(10, 8)

        img_path, img_name = self.gen_img_path()
        plt.savefig(img_path)

        ana_code_logger.info(" =========== 变量相关性分析结束 ===========")

        return img_name, IMAGE_URL

    def get_filter_data(self, df, filters):
        if not filters:
            return df

        for item in filters:
            col = item.get('col')
            op = item.get('op')
            val = item.get('val')

            if op == "==":
                df = df[df[col] == val]
            elif op == ">=":
                df = df[df[col] >= val]
            elif op == "<=":
                df = df[df[col] <= val]
            elif op == "!=":
                df = df[df[col] != val]
            elif op == ">":
                df = df[df[col] > val]
            elif op == "<":
                df = df[df[col] < val]
        return df

    def get_train_test_dataset(self, df):
        """
        获取测试和训练集
        """
        new_df = df.copy(deep=True)
        filters = self.form_data.get("train_dataset", [])

        new_df = self.get_filter_data(new_df, filters)
        return new_df

    def get_validate_dataset(self):
        """
        获取校验数据集
        """
        datasets = {}
        valiadate_datasets = self.form_data.get("validate_datasets", [])
        for item in valiadate_datasets:
            name = item.get("name")
            filters = item.get("filters")
            new_df = self.df.copy(deep=True)
            new_df = self.get_filter_data(new_df, filters)
            datasets[name] = new_df
        return datasets

    def get_dealed_df(self):
        """
        获取处理之后的数据 
        """
        df = self.get_df()
        df = self.deal_na(df)  # 处理缺失值
        df = self.deal_variable_box(df)  # 处理分箱
        df = self.deal_dummy_variable(df)  # 处理亚变量
        return df

    def get_log_path(self):
        """
        获取3个logger生成的日志的路径
        """
        analysis_id = self.form_data.get("analysis_id")
        if not analysis_id:
            analysis_id = str(uuid.uuid1())

        for logger in [ana_code_logger, ana_param_logger, ana_image_logger]:
            for handler in logger.handlers:
                handler.set_context(analysis_id)

        return analysis_id

    def excelAddSheet(self, dfs, outfile):
        """
        把多个df写到一个excel中
        """
        writer = pd.ExcelWriter(outfile, engine='xlsxwriter')

        for i, df in enumerate(dfs):
            ana_code_logger.info("i: %s  type(df): %s" % (i, type(df)))
            try:
                df.to_excel(writer, sheet_name="sheet%s" % (i+1))
            except Exception as exc:
                ana_code_logger.error("error: %s" % str(exc))
        writer.save()

    def train_models(self):
        """
        训练和测试模型
        """
        pass

    def gen_img_path(self):
        img_name = "%s.png" % (str(uuid.uuid1()))
        img_path = os.path.join(IMAGE_PATH, img_name)
        return img_path, img_name

    def output(self, data):
        X = data[self.x_col]
        Y = data[self.y_col]                            # 实际值

        pred_proba = self.model.predict_proba(X)
        pred_class = self.model.predict(X)

        pred_proba = DataFrame(pred_proba[:, 1])        # 概率
        pred_class = DataFrame(pred_class)              # 分类

        concat_df = pd.concat([pred_proba, pred_class, Y], axis=1)
        return concat_df
    
    def model_validation(self, df, model, title):
        try:

            valid_X = df[self.x_col]
            valid_Y = df[self.y_col[0]]
            valid_Y = np.array(valid_Y.tolist())

            valid_pred = model.predict(valid_X)
            ana_code_logger.info("valid_pred: %s " % valid_pred)
            ana_code_logger.info("type(valid_pred: %s)" % type(valid_pred))

            valid_proba = model.predict_proba(valid_X)

            # 混淆矩阵图
            f, ax = plt.subplots(1, 1, figsize=(4, 3))
            sns.heatmap(confusion_matrix(valid_Y, valid_pred), ax=ax, annot=True, fmt='2.0f')
            ax.set_title(title)

            plt.subplots_adjust(hspace=0.2, wspace=0.2)

            img_path, img_name = self.gen_img_path()
            plt.savefig(img_path)
            ana_image_logger.info("img_name: %s" % img_name)

            try:
                valid_Y = valid_Y.astype(int)
                ana_code_logger.info("np.unique(valid_Y): %s" % (np.unique(valid_Y)))

                valid_pred = valid_pred.astype(int)

                valid_precision, valid_recall, valid_thresholds = precision_recall_curve(valid_Y, valid_pred)
                ana_code_logger.info("valid_precision:%s, valid_recall:%s, valid_thresholds: %s" % (valid_precision, valid_recall, valid_thresholds))
            except Exception as exc:
                ana_code_logger.error("error: %s" % str(exc))

            valid_aupr = average_precision_score(valid_Y, valid_proba[:, 1], average="macro", sample_weight=None)
            ana_code_logger.info("valid_aupr: %s" % valid_aupr)

            valid_auc = roc_auc_score(valid_Y, valid_proba[:, 1], average="macro", sample_weight=None)
            ana_code_logger.info("valid_auc: %s" % valid_auc)

            valid_fpr, valid_tpr, valid_thres = roc_curve(valid_Y, valid_proba[:, 1], pos_label=1)
            ana_code_logger.info("valid_fpr:%s, valid_tpr:%s, valid_thres: %s" % (
                valid_fpr, valid_tpr, valid_thres))

            try:
                valid_ks = abs(valid_fpr - valid_tpr).max()
                ana_code_logger.info("valid_ks: %s" % valid_ks)
            except Exception as exc:
                ana_code_logger.error("error: %s" % str(exc))


            ana_param_logger.info(title)
            ana_param_logger.info('-------------------------------------')
            ana_param_logger.info('  Precision = %s              Recall = %s' % (str(round(valid_precision[1], 2)),
                                                                                 str(round(valid_recall[1], 2))))
            ana_param_logger.info('  AUPR = %s                  AUC = %s' % ( str(round(valid_aupr, 2), str(round(valid_auc, 2)))))
            ana_param_logger.info('  KS =  %s' % str(round(valid_ks, 2)))
            ana_param_logger.info('-------------------------------------' + '\n\n\n')

            return valid_precision, valid_recall, valid_aupr, valid_auc, valid_ks
        except Exception as exc:
            ana_code_logger.error("error: %s" % str(exc))


    def validate_models(self):
        """
        校验模型 
        """
        datas = self.get_validate_dataset()
        self.validate_datasets = datas.values()
        for name, data in datas.items():
            precision, recall, aupr, auc, ks = self.model_validation(data, model=self.model,
                                                                     title="Result  for  Validate data\n")

            ana_param_logger.info(
                "[name]:%s   precision:%s recall:%s  aupr:%s   auc:%s    ks:%s" % (name, precision, recall, aupr, auc,
                                                                                   ks))

    def run(self):
        status = True
        err_msg = log_dir_id = execl_sl = execl_bs = None
        try:
            log_dir_id = self.get_log_path()
            self.train_models()
            self.validate_models()

            # 生成输出的df
            train_df_exc = self.output(pd.concat([self.X_train, self.y_train], axis=1))
            test_df_exc = self.output(pd.concat([self.X_test, self.y_test], axis=1))

            validate_df_exc = [self.output(df) for df in self.validate_datasets]

            datas = {"sl": [train_df_exc, test_df_exc, validate_df_exc], "bs": [validate_df_exc]}

            execl_files = []
            for key, data in datas.items():
                filename = "%s_%s.xlsx" % (str(uuid.uuid1()), key)
                ana_code_logger.info("excel filenam: %s" % filename)

                execl_files.append(filename)
                file_path = os.path.join(config.get("UPLOAD_FOLDER"), filename)
                self.excelAddSheet(data, file_path)
            execl_sl, execl_bs = execl_files
        except Exception as exc:
            status = False
            err_msg = str(exc)
        return log_dir_id, execl_sl, execl_bs, status, err_msg


class Lasso(BaseSkModel):
    sk_type = 'lasso'

    def train_models(self):
        """
        训练和测试模型
        """
        df = self.get_dealed_df()
        data = self.get_train_test_dataset(df)
        self.lasso_lr(data)

        train_data = pd.concat([self.X_train, self.y_train], axis=1)
        test_data = pd.concat([self.X_test, self.y_test], axis=1)

        ana_code_logger.info("train_data:%s\n      test_data:%s\n" % (train_data.head(10), test_data.head(10)))

        precision, recall, aupr, auc, ks = self.model_validation(train_data, model=self.model,
                                                            title="Result  for  Train_data\n")
        ana_code_logger.info("train_data: precision:%s recall:%s  aupr:%s   auc:%s    ks:%s" % (precision, recall, aupr,
                                                                                                auc, ks))

        precision, recall, aupr, auc, ks = self.model_validation(test_data, model=self.model,
                                                                 title="Result  for  Train_data\n")
        ana_code_logger.info("test_data: precision:%s recall:%s  aupr:%s   auc:%s    ks:%s" % (precision, recall, aupr,
                                                                                                auc, ks))

        self.df = df

    def lasso_lr(self, df):
        """
        机器学习模型
        """
        model_params = self.form_data.get("model_param", {})
        test_size = model_params.get("train_test_split", {}).get("test_size", 0.3)
        n_splits = model_params.get("StratifiedKFold", {}).get("n_splits", 5)
        ana_code_logger.info("model_params: %s" % model_params)

        X = df[self.x_col]
        Y = df[self.y_col]

        train_X, test_X, train_Y, test_Y = train_test_split(X, Y, test_size=test_size, random_state=42)

        custom_cv = StratifiedKFold(n_splits=n_splits, random_state=100)
        model = LogisticRegressionCV(Cs=800, fit_intercept=True, cv=custom_cv, dual=False, penalty='l1',
                                     scoring='roc_auc', solver='liblinear', tol=0.0001, max_iter=100, class_weight=None,
                                     n_jobs=4, verbose=0, refit=True, random_state=123)

        model.fit(train_X, train_Y)

        # 变量重要性
        row_num, col_num = train_X.shape
        lr_coef = model.coef_
        lr_coef_reshp = lr_coef.reshape(col_num, )
        n_top = col_num
        top_vars_index = abs(lr_coef_reshp).argsort()[::-1][:n_top]
        top_vars_coef = lr_coef_reshp[top_vars_index]
        top_vars_names = np.array(train_X.columns[top_vars_index])
        top_vars_label = ['S%d' % (i + 1) for i in np.arange(n_top)]
        output_coef = pd.DataFrame(
            {'Top_var_label': top_vars_label, 'Top_var_name': top_vars_names, 'Top_var_coef': top_vars_coef})
        output_coef = output_coef.reindex(columns=['Top_var_label', 'Top_var_name', 'Top_var_coef'])

        ana_param_logger.info(output_coef)

        self.model = model
        self.X_train = train_X
        self.X_test = test_X
        self.y_train = train_Y
        self.y_test = test_Y


class GeneraLR(BaseSkModel):
    """
    普通逻辑回归
    """
    sk_type = 'genera_lr'

    def lr_model(self, df):

        model_params = self.form_data.get("model_param")
        ana_code_logger.info("model_params: %s" % model_params)

        X = df[self.x_col]
        y = df[self.y_col]

        test_size = model_params.get("train_test_split").get("test_size")
        random_state = model_params.get("train_test_split").get("random_state")
        stratify = model_params.get("train_test_split").get("stratify")
        explanatory_cols = model_params.get("extra").get("explanatory_cols")

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state,
                                                            stratify=df[stratify])

        X_train_intercept = np.concatenate(
            [np.ones(X_train.shape[0]).reshape(X_train.shape[0], 1), X_train[explanatory_cols]], axis=1)
        X_test_intercept = np.concatenate(
            [np.ones(X_test.shape[0]).reshape(X_test.shape[0], 1), X_test[explanatory_cols]], axis=1)

        lr_model = sm.Logit(y_train, X_train_intercept)
        lr_model_results = lr_model.fit()
        ana_param_logger.info('LR Model Summary: \n')

        ana_param_logger.info(lr_model_results.summary2())

        utility_scores_tr = np.dot(X_train_intercept, lr_model_results.params.values)
        utility_scores_ts = np.dot(X_test_intercept, lr_model_results.params.values)

        lr_pred_probs_tr = np.exp(utility_scores_tr) / (1.0 + np.exp(utility_scores_tr))
        lr_pred_probs_ts = np.exp(utility_scores_ts) / (1.0 + np.exp(utility_scores_ts))

        ana_param_logger.info('AUC on training data... \n')
        ana_param_logger.info(roc_auc_score(y_train, lr_pred_probs_tr))
        ana_param_logger.info('\nAUC on testing data... \n')
        ana_param_logger.info(roc_auc_score(y_test, lr_pred_probs_ts))

        ap_tr = average_precision_score(y_train, lr_pred_probs_tr)
        ap_ts = average_precision_score(y_test, lr_pred_probs_ts)

        ana_param_logger.info('AUPR on training data is %5.3f ... \n' % ap_tr)
        ana_param_logger.info('\nAUPR on testing data is %5.3f ... \n' % ap_ts)

        lr_pred_label_tr = pd.Series(lr_pred_probs_tr).apply(lambda x: 1 if x > 0.5 else 0)
        lr_pred_label_ts = pd.Series(lr_pred_probs_ts).apply(lambda x: 1 if x > 0.5 else 0)
        ana_param_logger.info('Precison on training data is %5.3f ... \n' % precision_score(y_train, lr_pred_label_tr))
        ana_param_logger.info('Recall on training data is %5.3f ... \n' % recall_score(y_train, lr_pred_label_tr))
        ana_param_logger.info('Precison on test data is %5.3f ... \n' % precision_score(y_test, lr_pred_label_ts))
        ana_param_logger.info('Recall on test data is %5.3f ... \n' % recall_score(y_test, lr_pred_label_ts))

        self.X_train = X_train
        self.X_test = X_test
        self.y_train = y_train
        self.y_test = y_test
        self.model = lr_model_results

    def train_models(self):
        """
        训练和测试模型
        """
        df = self.get_dealed_df()
        data = self.get_train_test_dataset(df)
        self.lr_model(data)


class MixedLR(BaseSkModel):
    """
    混合逻辑回归
    """
    sk_type = 'mixed_lr'
    r_file = 'mixed_sk_model.R'

    def train_test_dataset(self):
        df = self.get_df()
        data = self.get_train_test_dataset(df)

        model_params = self.form_data.get("model_param")
        ana_code_logger.info("model_params: %s" % model_params)

        self.x_col = model_params.get("dataset", {}).get("x_col")
        self.y_col = model_params.get("dataset", {}).get("y_col")
        self.extra_factor = model_params.get("extra", {}).get("extra_factor")

        X = data[self.x_col]
        y = df[self.y_col]

        test_size = model_params.get("train_test_split").get("test_size")
        random_state = model_params.get("train_test_split").get("random_state")
        stratify = model_params.get("train_test_split").get("stratify")

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state,
                                                            stratify=X[stratify])

        self.df = df
        return X_train, X_test, y_train, y_test

    def calculate_model_param(self, real, predicted):
        """
        模型auc, roc, recall计算
        """
        # 计算训练集auc
        train_auc = roc_auc_score(real, predicted, average="macro", sample_weight=None)

        ana_param_logger.info("data auc: %s" % train_auc)

        # 计算混淆矩阵
        f, ax = plt.subplots(1, 1, figsize=(4, 3))
        sns.heatmap(confusion_matrix(real, predicted), ax=ax, annot=True,
                    fmt='2.0f')
        ax.set_title("confusion matrix")

        plt.subplots_adjust(hspace=0.2, wspace=0.2)

        img_path, img_name = self.gen_img_path()
        plt.savefig(img_path)
        ana_param_logger.info("img_name: %s" % img_name)

        valid_precision, valid_recall, valid_thresholds = precision_recall_curve(real, predicted)

        ana_param_logger.info('  Precision = ', str(round(valid_precision[1], 2)), '  Recall = ',
                              str(round(valid_recall[1], 2)))

    def deal_data(self, data):
        random_effects = self.model_rest.get("random_effects")  # 随机效应
        ana_code_logger.info("随机效应: random_effects:%s" % random_effects.head(10))

        # left_join
        X_test = data.join(random_effects, on=self.extra_factor, how="left")
        ana_code_logger.info("X_test left joined random_effects: %s" % X_test.head(10))

        # left join后去空
        if X_test.isnull().sum().sum() > 0:
            X_test = X_test.dropna()

        # 计算测试集的score
        fixed_effects = self.model_rest.get("fixed_effects")
        score = np.zeros(X_test.shape[0])

        for name, v in X_test.items():
            score += v * fixed_effects[name]

        score += score + fixed_effects["(Intercept)"]
        score = score.reshape(X_test.shape[0], 1)

        X_test['score'] = score

        # 计算测试集预测概率
        X_test['pred_probs'] = np.exp(score) / (np.exp(score) + 1)
        ana_code_logger.info("预测概率: %s" % X_test.head(10))

        # 计算模型参数
        self.calculate_model_param(self.y_test, X_test['pred_probs'])
        return X_test

    def aggregate(self, data):
        # 计算18春-18暑预测续报结果

        df = self.df.join(data, on='student_id', how='left')

        def transfer(v):
            return 1 if v > 0.5 else 0

        df['pred_is_continued'] = df['pred_probs'].apply(transfer)
        ana_code_logger.info("聚合到机构维度： df: %s" % df)

        # 计算预测发生率与实际发生率的MSE，RMSE
        ins_pred_probs = df.groupby('ins_id')['pred_probs'].mean()       # 机构预测平均概率
        ins_event_probs = df.groupby('ins_id')['is_continued'].mean()         # 机构实际平均预测概率

        ins_continued_prob_data = pd.concat([ins_pred_probs, ins_event_probs], axis=1)
        ana_code_logger.info("机构预测发生率与实际发生率：%s" % ins_continued_prob_data)

        mse = np.power((ins_event_probs - ins_pred_probs), 2).sum()/ins_continued_prob_data.shape[0]
        ana_code_logger.info("MSE: %s" % mse)

        rmse = np.sqrt(mse)
        ana_code_logger.info("RMSE: %s" % rmse)

        # 机构维度续报实际结果
        actual_continued_num = df.groupby('ins_id')['is_continued'].sum()         # 计算每个机构实际续报人数
        pred_continued_num = df.groupby('ins_id')['pred_is_continued'].sum()         # 预测续报人数

        total_student = df.groupby('ins_id')['student_id'].count()

        # 计算机构实际续报率：actual_rate=实际续报人数(actual_continued_num)/总人数(num)
        ins_continued_result_data = pd.DataFrame()

        ins_continued_result_data['actual_rate'] = actual_continued_num/total_student
        ins_continued_result_data['pred_rate'] = pred_continued_num/total_student

        ana_code_logger.info("ins_continued_result_data: %s" % ins_continued_result_data.head(10))

        ins_mse = np.power((ins_continued_result_data['actual_rate'] - ins_continued_result_data['pred_rate']), 2)\
                      .sum()/ins_continued_result_data.shape[0]
        ana_code_logger.info("ins_mse: %s" % ins_mse)

        ins_rmse = np.sqrt(ins_mse)
        ana_code_logger.info("ins_rmse: %s" % ins_rmse)

    def run_train(self):
        filename = os.path.join(R_MODEL_FILE, self.r_file)
        robjects.r.source(filename)

        # 参数
        self.X_train, self.X_test, self.y_train, self.y_test = self.train_test_dataset()

        X_train_r = pandas2ri.py2ri(self.X_train)
        predictors_vec = robjects.StrVector(self.x_col)

        model_rest = robjects.r.lr_mixed_model(model_data=X_train_r, subject_id=self.extra_factor, response=self.y_col,
                                  predictors_vec=predictors_vec, random_intercept=True)

        rest = {}
        for i, name in enumerate(model_rest):
            rest[name] = pandas2ri.ri2py(model_rest[i])

        ana_code_logger.info("train data ==> model return value: %s" % rest)

        # 合并数据
        self.X_train = pd.concat(self.X_train, rest.get("predicted_probabilities"))

        # 计算模型参数
        self.calculate_model_param(self.y_train, self.X_train['predicted_probs_with_rand'])

        self.model_rest = model_rest

    def run_test(self):
        """
        测试集 
        """
        ana_code_logger.info("测试集日志：\n")
        self.X_test = self.deal_data(self.X_test)

        self.X_train['pred_probs'] = self.X_train['predicted_probs_with_rand']

        stu_result = pd.concat(self.X_train[['student_id', 'pred_probs']], self.X_test[['student_id', 'pred_probs']])

        self.aggregate(stu_result)

    def run_validate(self):
        """
        验证集 
        """
        ana_code_logger.info("验证集日志：\n")
        datasets = self.get_validate_dataset()
        self.validate_datasets = datasets.values()

        for data in self.validate_datasets:
            data = self.deal_data(data)

            data['pred_probs'] = data['predicted_probs_with_rand']

            stu_result = pd.concat(data[['student_id', 'pred_probs']], data[['student_id', 'pred_probs']])

            self.aggregate(stu_result)

    def run(self):
        status = True
        err_msg = log_dir_id = execl_sl = execl_bs = None
        try:
            log_dir_id = self.get_log_path()
            self.run_train()
            self.run_test()
            self.run_validate()

            # 生成输出的df
            train_df_exc = self.output(self.X_train)
            test_df_exc = self.output(self.X_test)

            validate_df_exc = [self.output(df) for df in self.validate_datasets]

            datas = {"sl": [train_df_exc, test_df_exc, validate_df_exc], "bs": [validate_df_exc]}

            execl_files = []
            for key, data in datas.items():
                filename = "%s_%s.xlsx" % (str(uuid.uuid1()), key)
                execl_files.append(filename)
                file_path = os.path.join(config.get("UPLOAD_FOLDER"), filename)
                self.excelAddSheet(data, file_path)
            execl_sl, execl_bs = execl_files
        except Exception as exc:
            status = False
            err_msg = str(exc)
        return log_dir_id, execl_sl, execl_bs, status, err_msg

























sk_types = {
    o.sk_type: o for o in globals().values()
    if (
        inspect.isclass(o) and
        issubclass(o, BaseSkModel) and
        o.sk_type not in config.get('VIZ_TYPE_BLACKLIST'))}
