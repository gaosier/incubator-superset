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


config = app.config
logger = logging.getLogger('analysis')

METRIC_KEYS = [
    'metric', 'metrics', 'percent_metrics', 'metric_2', 'secondary_metric',
    'x', 'y', 'size',
]

IMAGE_URL = config.get("IMG_UPLOAD_URL")


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
        self.request = request
        self.sk_type = form_data.get("sk_type")
        self.form_data = form_data

        self.query = BASE_QUERY + self.datasource.table_name + ';'

        # 跑模型所需的参数
        self.df = None
        self.model = None

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
        operate_info = self.form_data.get("null_operate")
        operate = operate_info.get("operate")
        if not operate:
            raise SupersetParamException(u"参数[operate]不能为空")
        detail = operate_info.get("detail")
        fillna = self.get_column_fillna(df, detail)

        if operate == "fill":
            df = df.fillna(fillna)
        else:
            df = df.dropna()
        return df

    def deal_variable_box(self, df):
        """
        变量分箱处理
        """
        variable_box = self.form_data.get("variable_box")
        for item in variable_box:
            field = item.get("field")
            bins = item.get("bins")
            labels = item.get("labels")
            if not field or (not bins) or (not labels):
                return df
            col = pd.cut(df[field], bins=bins, labels=labels)
            df[field] = col
        return df

    def deal_dummy_variable(self, df):
        """
        哑变量处理
        """
        dummy_variable = self.form_data.get("dummy_variable")
        for field, value in dummy_variable.items():
            df[field] = df[field].map(value)
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
        img_name = "%s.png" % str(uuid.uuid1())
        img_path = IMAGE_URL + img_name
        correlation_analysis = self.form_data.get("correlation_analysis")
        count = len(correlation_analysis)

        if count < 3:
            row = 1
        else:
            row = count//3 if count % 3 == 0 else count //3 + 1

        fig, ax = plt.subplots(row, 3, figsize=(7, 3))
        count = -1
        for field, func, chart in correlation_analysis:
            count += 1
            if func == 'matplotlib'  and chart == 'pie':
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
        plt.savefig(img_path)
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
        train_dataset = self.form_data.get("train_dataset", {})
        filters = train_dataset.get("filters")
        fields = train_dataset.get("fields")

        new_df = self.get_filter_data(new_df, filters)
        new_df = new_df[fields]
        return new_df

    def get_validate_dataset(self, df):
        """
        获取校验数据集
        """
        datasets = []
        valiadate_datasets = self.form_data.get("validate_datasets", {})
        for name, info in valiadate_datasets.items():
            new_df = df.copy(deep=True)
            filters = info.get("filters")
            fields = info.get("fields")
            new_df = self.get_filter_data(new_df, filters)
            new_df = new_df[fields]
            datasets.append(new_df)
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
            analysis_id = uuid.uuid1()

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
            df.to_excel(writer, sheet_name="sheet%s" % (i+1))
        writer.save()

    def train_models(self):
        """
        训练和测试模型
        """
        pass

    def validate_models(self):
        """
        验证模型
        :return: 
        """
        pass

    def run(self):
        return []


class Lasso(BaseSkModel):
    sk_type = 'lasso'

    def train_models(self):
        df = self.get_dealed_df()
        data = self.get_train_test_dataset(df)
        model, train_data, test_data = self.lasso_lr(data)
        ana_code_logger.info("model: %s    train_data:%s      test_data:%s" % (model, train_data, test_data))

        precision, recall, aupr, auc, ks = self.model_validation(train_data, model=model,
                                                            title="Result  for  Train_data\n")
        ana_code_logger.info("train_data: precision:%s recall:%s  aupr:%s   auc:%s    ks:%s" % (precision, recall, aupr, auc, ks))

        self.df = df
        self.model = model
        return train_data, test_data

    def validate_models(self):
        datas = self.get_validate_dataset(self.df)
        for data in datas:
            precision, recall, aupr, auc, ks = self.model_validation(data, model=self.model,
                                                                     title="Result  for  Train_data\n")

            ana_param_logger.info(
                "[data]:%s   precision:%s recall:%s  aupr:%s   auc:%s    ks:%s" % (data, precision, recall, aupr, auc,
                                                                                   ks))
        return datas

    def output(self, data):
        X = data[data.columns[1:]]
        Y = data[data.columns[:1]]

        pred_proba = self.model.predict_proba(X)
        pred_class = self.model.predict(X)

        pred_proba = DataFrame(pred_proba[:, 1])        # 概率
        pred_class = DataFrame(pred_class)              # 分类
        Y = DataFrame(Y)                                # 实际值

        concat_df = pd.concat([pred_proba, pred_class, Y], axis=1)
        return concat_df

    def lasso_lr(self, df):
        """
        机器学习模型
        """
        X = df[df.columns[1:]]
        Y = df[df.columns[:1]]

        model_params = self.form_data.get("model_param", {})
        test_size = model_params.get("train_test_split", {}).get("test_size", 0.3)
        n_splits = model_params.get("StratifiedKFold", {}).get("n_splits", 5)
        ana_code_logger.info("model_params: %s" % model_params)

        train_X, test_X, train_Y, test_Y = train_test_split(X, Y, test_size=test_size, random_state=42)

        custom_cv = StratifiedKFold(n_splits=n_splits, random_state=100)
        model = LogisticRegressionCV(Cs=800, fit_intercept=True, cv=custom_cv, dual=False, penalty='l1',
                                     scoring='roc_auc', solver='liblinear', tol=0.0001, max_iter=100, class_weight=None,
                                     n_jobs=4, verbose=0, refit=True, random_state=123)
        model.fit(train_X, train_Y)

        train_data = pd.concat([train_Y, train_X], axis=1)
        test_data = pd.concat([test_Y, test_X], axis=1)

        # 变量重要性
        row_num, col_num = shape(train_X)
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

        return model, train_data, test_data

    def model_validation(self, df, model, title):
        valid_X = df[df.columns[1:]]
        valid_Y = df[df.columns[:1]]

        valid_pred = model.predict(valid_X)
        valid_proba = model.predict_proba(valid_X)

        # 混淆矩阵图
        f, ax = plt.subplots(1, 1, figsize=(4, 3))
        sns.heatmap(confusion_matrix(valid_Y, valid_pred), ax=ax, annot=True, fmt='2.0f')
        ax.set_title(title)

        plt.subplots_adjust(hspace=0.2, wspace=0.2)
        plt.show()

        valid_precision, valid_recall, valid_thresholds = precision_recall_curve(valid_Y, valid_pred)
        valid_aupr = average_precision_score(valid_Y, valid_proba[:, 1], average="macro", sample_weight=None)
        valid_auc = roc_auc_score(valid_Y, valid_proba[:, 1], average="macro", sample_weight=None)
        valid_fpr, valid_tpr, valid_thres = roc_curve(valid_Y, valid_proba[:, 1], pos_label=1)
        valid_ks = abs(valid_fpr - valid_tpr).max()

        ana_param_logger.info(title)
        ana_param_logger.info('-------------------------------------')
        ana_param_logger.info('  Precision = ', str(round(valid_precision[1], 2)), '  Recall = ', str(round(valid_recall[1], 2)))
        ana_param_logger.info('  AUPR = ', str(round(valid_aupr, 2)), '      AUC = ', str(round(valid_auc, 2)))
        ana_param_logger.info('  KS = ', str(round(valid_ks, 2)))
        ana_param_logger.info('-------------------------------------' + '\n\n\n')

        return valid_precision, valid_recall, valid_aupr, valid_auc, valid_ks

    def run(self):
        status = True
        err_msg = log_dir_id = execl_sl = execl_bs = None
        try:
            log_dir_id = self.get_log_path()
            train_df, test_df = self.train_models()
            validate_dfs = self.validate_models()

            # 生成输出的df
            train_df_exc = self.output(train_df)
            test_df_exc = self.output(test_df)

            validate_df_exc = [self.output(df) for df in validate_dfs]

            datas = {"sl": [train_df_exc, test_df_exc, validate_df_exc], "bs": [validate_df_exc]}

            execl_files = []
            for key, data in datas.items():
                filename = "%s_%s.xlsx" % (str(uuid.uuid1()), key)
                execl_files.append(filename)
                file_path = os.path.join(config.get("UPLOAD_FOLDER"), filename)
                self.excelAddSheet(data, file_path)
            execl_sl , execl_bs = execl_files
        except Exception as exc:
            status = False
            err_msg = str(exc)
        return log_dir_id, execl_sl, execl_bs, status, err_msg


class GeneraLR(BaseSkModel):
    """
    普通逻辑回归
    """
    sk_type = 'genera_lr'

    def lr_model(self, df):

        model_params = self.form_data.get("model_param")
        ana_code_logger.info("model_params: %s" % model_params)
        y_col = model_params.get("train_test_split").get("y_col")
        y = df[y_col]

        test_size = model_params.get("train_test_split").get("test_size")
        random_state = model_params.get("train_test_split").get("random_state")
        stratify = model_params.get("train_test_split").get("stratify")
        explanatory_cols = model_params.get("extra").get("explanatory_cols")

        X_train, X_test, y_train, y_test = train_test_split(df, y, test_size=test_size, random_state=random_state,
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

        return {'LR_Model': lr_model_results}

    def train_models(self):
        """
        训练和测试模型
        """
        df = self.get_dealed_df()
        data = self.get_train_test_dataset(df)
        self.lr_model(data)

    def validate_models(self):
        pass

    def run(self):
        """
        运行模型
        """
        self.train_models()


class MixedLR(object):
    """
    混合逻辑回归
    """
    sk_type = 'mixed_lr'




sk_types = {
    o.sk_type: o for o in globals().values()
    if (
        inspect.isclass(o) and
        issubclass(o, BaseSkModel) and
        o.sk_type not in config.get('VIZ_TYPE_BLACKLIST'))}
