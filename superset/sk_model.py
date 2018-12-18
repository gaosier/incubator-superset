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

from rpy2.robjects import pandas2ri
from rpy2.robjects.methods import RS4
from pandas.core.frame import DataFrame
from sklearn.linear_model import LogisticRegressionCV
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.metrics import (confusion_matrix, precision_recall_curve, average_precision_score, roc_auc_score,
                             roc_curve, precision_score, recall_score, auc)


from superset import app
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

class ExpressionSet(RS4):
    pass


def change(x):
    if x > 0.5:
        return 1
    else:
        return 0


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
        self.master_factor = None       # 混合模型所需的参数
        self.slave_factor = None
        self.predictors_vec = None

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
        if not self.x_col or not self.y_col:
            raise ValueError("模型参数[x_col]或则[y_col]为空！！！")

        self.y_col = self.y_col[0]

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
        ana_code_logger.info("============= 缺失值处理结束 =================")
        return df

    def str_to_list(self, val):
        if isinstance(val, str):
            val = val.replace(' ', '').strip()     # 去空值
            val = val.split(',')

            for i, item in enumerate(val):
                try:
                    item = int(item)
                except:
                    item = float(item)
                val[i] = item
        return val

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
            right = item.get("right", True)
            left = item.get("left", True)

            bins = self.str_to_list(bins)
            labels = self.str_to_list(labels)

            if not field or (not bins) or (not labels):
                return df
            col = pd.cut(df[field], bins=bins, labels=labels, right=right, include_lowest=left)
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
            elif func == 'seaborn' and chart == 'heatmap':
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
        ana_code_logger.info("[训练集和测试集]: shape:%s\n      head(10): %s\n" % (str(new_df.shape), new_df.head(10)))
        return new_df

    def get_validate_dataset(self):
        """
        获取校验数据集
        """
        datasets = {}
        valiadate_datasets = self.form_data.get("validate_datasets", [])
        ana_code_logger.info("self.form_data.get(valiadate_datasets): %s" % valiadate_datasets)
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
            if df is not None:
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
            valid_Y = df[self.y_col]
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
                valid_recall = 0.0
                valid_precision = 0.0
                ana_code_logger.error("error: %s" % str(exc))

            valid_aupr = average_precision_score(valid_Y, valid_proba[:, 1], average="macro", sample_weight=None)
            ana_code_logger.info("valid_aupr: %s     type(valid_aupr): %s" % (valid_aupr, type(valid_aupr)))

            valid_auc = roc_auc_score(valid_Y, valid_proba[:, 1], average="macro", sample_weight=None)
            ana_code_logger.info("valid_auc: %s  type(valid_auc): %s " % (valid_auc, type(valid_auc)))

            valid_fpr, valid_tpr, valid_thres = roc_curve(valid_Y, valid_proba[:, 1], pos_label=1)
            ana_code_logger.info("valid_fpr:%s, valid_tpr:%s, valid_thres: %s" % (
                valid_fpr, valid_tpr, valid_thres))

            try:
                valid_ks = abs(valid_fpr - valid_tpr).max()
                ana_code_logger.info("valid_ks: %s" % valid_ks)
            except Exception as exc:
                valid_ks = 0.0
                ana_code_logger.error("error: %s" % str(exc))

            ana_param_logger.info(title)
            ana_param_logger.info('-------------------------------------')
            ana_param_logger.info('  Precision = %s              Recall = %s' % (round(valid_precision[1], 2),
                                                                                 round(valid_recall[1], 2)))
            ana_param_logger.info('  AUPR = %s                  AUC = %s' % (round(valid_aupr, 2), round(valid_auc, 2)))
            ana_param_logger.info('  KS =  %s' % round(valid_ks, 2))
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
            ana_code_logger.error("error: %s" % exc)
        return log_dir_id, execl_sl, execl_bs, status, err_msg

    def output_data_to_excel(self, X_train=None, X_test=None, y_train=None, y_test=None, filename=None):
        if X_train is not None and y_train is not None:
            train_data = pd.concat([X_train, y_train], axis=1)
        else:
            train_data = X_train
        if X_test is not None and y_test is not None:
            test_data = pd.concat([X_test, y_test], axis=1)
        else:
            test_data = X_test

        dfs = [train_data, test_data]
        file_path = os.path.join(config.get("UPLOAD_FOLDER"), filename)
        self.excelAddSheet(dfs, file_path)


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
                                                                 title="Result  for  Test_data\n")
        ana_code_logger.info("test_data: precision:%s recall:%s  aupr:%s   auc:%s    ks:%s" % (precision, recall, aupr,
                                                                                                auc, ks))

        self.df = df

    def lasso_lr(self, df):
        """
        机器学习模型
        """
        ana_code_logger.info("self.form_data:%s" % self.form_data)
        model_params = self.form_data.get("model_param", {})
        test_size = model_params.get("train_test_split", {}).get("test_size", 0.3)
        n_splits = model_params.get("StratifiedKFold", {}).get("n_splits", 5)
        ana_code_logger.info("model_params: %s" % model_params)

        X = df[self.x_col]
        Y = df[self.y_col]

        ana_code_logger.info("X.isnull().sum(): %s" % X.isnull().sum())
        ana_code_logger.info("Y.isnull().sum(): %s" % Y.isnull().sum())
        ana_code_logger.info("X.shape: %s    Y.shape:%s " % (str(X.shape), str(Y.shape)))

        train_X, test_X, train_Y, test_Y = train_test_split(X, Y, test_size=test_size, random_state=42)
        ana_code_logger.info("train_test_split data success !!!")

        custom_cv = StratifiedKFold(n_splits=n_splits, random_state=100)
        model = LogisticRegressionCV(Cs=800, fit_intercept=True, cv=custom_cv, dual=False, penalty='l1',
                                     scoring='roc_auc', solver='liblinear', tol=0.0001, max_iter=100, class_weight=None,
                                     n_jobs=4, verbose=0, refit=True, random_state=123)

        ana_code_logger.info("train_X.shape: %s     train_Y.shape: %s" % (str(train_X.shape), str(train_Y.shape)))

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

        # self.output_data_to_excel(X_train, X_test, y_train, y_test, 'genera_test.xlsx')

        X_train_intercept = np.concatenate(
            [np.ones(X_train.shape[0]).reshape(X_train.shape[0], 1), X_train[explanatory_cols].values], axis=1)
        ana_code_logger.info("type(X_train_intercept): %s " % (type(X_train_intercept)))

        X_test_intercept = np.concatenate(
            [np.ones(X_test.shape[0]).reshape(X_test.shape[0], 1), X_test[explanatory_cols].values], axis=1)
        ana_code_logger.info("type(X_test_intercept): %s " % (type(X_test_intercept)))

        lr_model = sm.Logit(y_train.astype(float), X_train_intercept.astype(float))
        lr_model_results = lr_model.fit()
        ana_param_logger.info('LR Model Summary: \n')

        ana_param_logger.info(lr_model_results.summary2())

        utility_scores_tr = np.dot(X_train_intercept, lr_model_results.params.values).astype(float)
        ana_code_logger.info("utility_scores_tr.dtype: %s" % utility_scores_tr.dtype)

        utility_scores_ts = np.dot(X_test_intercept, lr_model_results.params.values).astype(float)
        ana_code_logger.info("utility_scores_ts.dtype: %s" % utility_scores_ts.dtype)

        lr_pred_probs_tr = np.exp(utility_scores_tr) / (1 + np.exp(utility_scores_tr))
        lr_pred_probs_ts = np.exp(utility_scores_ts) / (1 + np.exp(utility_scores_ts))

        ana_param_logger.info('AUC on training data:  %s\n  ' % roc_auc_score(y_train, lr_pred_probs_tr))
        ana_param_logger.info('AUC on testing data: %s\n  ' % roc_auc_score(y_test, lr_pred_probs_ts))


        ana_code_logger.info("y_train: %s" % np.unique(y_train))
        ap_tr = average_precision_score(y_train.astype(float), lr_pred_probs_tr)
        ap_ts = average_precision_score(y_test.astype(float), lr_pred_probs_ts)

        ana_param_logger.info('AUPR on training data is %s\n' % round(ap_tr, 3))
        ana_param_logger.info('AUPR on testing data is %s\n' % round(ap_ts, 3))

        lr_pred_label_tr = pd.Series(lr_pred_probs_tr).apply(lambda x: 1 if x > 0.5 else 0)
        lr_pred_label_ts = pd.Series(lr_pred_probs_ts).apply(lambda x: 1 if x > 0.5 else 0)
        ana_param_logger.info('Precison on training data is: %s \n' % round(precision_score(y_train.astype(float),lr_pred_label_tr), 3))
        ana_param_logger.info('Recall on training data is: %s \n' % round(recall_score(y_train.astype(float), lr_pred_label_tr), 3))
        ana_param_logger.info('Precison on test data is: %s \n' % round(precision_score(y_test.astype(float), lr_pred_label_ts), 3))
        ana_param_logger.info('Recall on test data is: %s \n' % round(recall_score(y_test.astype(float), lr_pred_label_ts),3))

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

    def run(self):
        status = True
        err_msg = log_dir_id = execl_sl = execl_bs = None
        try:
            log_dir_id = self.get_log_path()
            self.train_models()
            self.validate_models()

            # 生成输出的df
            train_df_exc = pd.concat([self.X_train, self.y_train], axis=1)
            test_df_exc = pd.concat([self.X_test, self.y_test], axis=1)

            validate_df_exc = [df for df in self.validate_datasets]

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
            ana_code_logger.error("error: %s" % exc)
        return log_dir_id, execl_sl, execl_bs, status, err_msg


class MixedLR(BaseSkModel):
    """
    混合模型
    """
    sk_type = 'mixed_lr'
    r_file = 'mixed_sk_model.R'

    def train_test_dataset(self):
        df = self.get_df()
        data = self.get_train_test_dataset(df)

        model_params = self.form_data.get("model_param")
        ana_code_logger.info("model_params: %s" % model_params)

        self.master_factor = model_params.get("extra", {}).get("master_factor", [])
        self.slave_factor = model_params.get("extra", {}).get("slave_factor", [])
        self.predictors_vec = model_params.get("extra", {}).get("predictors_vec")

        if not self.master_factor or not self.slave_factor or not self.predictors_vec:
            raise ValueError("模型参数不能为空！！！")

        self.slave_factor = self.slave_factor[0]
        self.master_factor = self.master_factor[0]

        X = data[self.x_col]
        y = df[self.y_col]

        ana_code_logger.info("原始数据的数据量：X.shape:%s       Y.shape: %s" % ( str(X.shape), str(y.shape)))
        ana_code_logger.info("X.isnull().sum(): %s" % X.isnull().sum())

        test_size = model_params.get("train_test_split").get("test_size")
        random_state = model_params.get("train_test_split").get("random_state")
        stratify = model_params.get("train_test_split").get("stratify")

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state,
                                                            stratify=df[stratify])

        # self.output_data_to_excel(X_train, X_test, y_train, y_test, 'R_model_data.xlsx')

        self.df = df
        return X_train, X_test, y_train, y_test

    def calculate_model_param(self, real, predicted, title='train'):
        """
        模型auc, roc, recall计算
        """
        # 计算训练集auc
        try:
            auc = roc_auc_score(real, predicted)
            ana_param_logger.info("[%s]数据集   auc: %s" % (title, auc))

        except Exception as exc:
            ana_code_logger.error("error: %s" % str(exc))
            raise ValueError(str(exc))

        # 计算混淆矩阵
        f, ax = plt.subplots(1, 1, figsize=(4, 3))
        sns.heatmap(confusion_matrix(real, predicted), ax=ax, annot=True, fmt='2.0f')
        ax.set_title("confusion matrix")

        plt.subplots_adjust(hspace=0.2, wspace=0.2)

        img_path, img_name = self.gen_img_path()
        plt.savefig(img_path)
        ana_image_logger.info("[%s]  img_name: %s" % (title, img_name))

        valid_precision, valid_recall, valid_thresholds = precision_recall_curve(real, predicted)

        ana_param_logger.info('[%s]  Precision =  %s        Recall = %s' % (title, round(valid_precision[1], 4),
                                                                        round(valid_recall[1], 4)))

    def deal_data(self, data):
        random_effects = self.model_rest.get("random_effects")  # 随机效应
        ana_code_logger.info("[随机效应] ====> random_effects:\n %s\n" % random_effects.head(10))

        # 合并数据集
        X_test= pd.merge(data, random_effects, on=self.master_factor, how='left')

        # left join后去空
        if X_test.isnull().sum().sum() > 0:
            ana_code_logger.info("[随机效应合并之后的数据的空值]:\n %s\n" % X_test.isnull().sum().sum())
            X_test = X_test.dropna()

        ana_code_logger.info("[随机效应合并之后的数据集]:\n %s\n" % X_test.head(10))

        # 计算测试集的score
        fixed_effects = self.model_rest.get("fixed_effects")
        ana_code_logger.info("[固定效应] ===> fixed_effects: %s" % fixed_effects)

        new_fixed_effects = {}
        count = 0
        for name in self.predictors_vec:
            count += 1
            new_fixed_effects[name] = fixed_effects[count]

        pre_test = X_test[self.predictors_vec]
        ana_code_logger.info("[预测变量数据集]:\n %s\n" % str(pre_test.shape))

        ana_code_logger.info("======= 计算测试集的score ============")
        score = []

        for item in pre_test.to_dict(orient="records"):
            ele = 0.0
            for k, v in item.items():
                ele += v * new_fixed_effects[k]
            score.append(ele)

        score = np.array(score)
        score = score + fixed_effects[0]
        score = score + X_test["intercept_random_part"]
        X_test['score'] = score

        # 计算测试集预测概率
        X_test['pred_probs'] = np.exp(score) / (np.exp(score) + 1)
        ana_code_logger.info("[得到预测概率之后的数据集]:\n %s\n" % X_test.head(10))

        #self.output_data_to_excel(X_test=X_test, filename='r_test_data.xlsx')

        # 计算模型参数
        self.calculate_model_param(self.y_test, X_test['pred_probs'].apply(change), title='test')
        return X_test

    def aggregate(self, data):
        # 计算18春-18暑预测续报结果
        ana_code_logger.info("self.df.shape: %s        data.shape: %s" % (str(self.df[self.x_col].shape),
                                                                          str(data.shape)))
        ana_code_logger.info("self.x_col: %s         self.y_col: %s" % (self.x_col, self.y_col))
        cols = self.x_col + [self.y_col]
        ana_code_logger.info("all columns: %s       df.columns: %s" % (cols, self.df.columns))

        df = pd.merge(self.df[cols], data, on=self.slave_factor, how='left')
        ana_code_logger.info("df.shape: %s" % str(df.shape))

        df['pred_is_continued'] = df['pred_probs'].apply(change)
        ana_code_logger.info("聚合到机构维度： df: %s" % df)

        # 计算预测发生率与实际发生率的MSE，RMSE
        ins_pred_probs = df.groupby(self.master_factor)['pred_probs'].mean()       # 机构预测平均概率
        ins_event_probs = df.groupby(self.master_factor)['is_continued'].mean()         # 机构实际平均预测概率

        ins_continued_prob_data = pd.concat([ins_pred_probs, ins_event_probs], axis=1)
        ana_code_logger.info("机构预测发生率与实际发生率：%s" % ins_continued_prob_data)

        mse = np.power((ins_event_probs - ins_pred_probs), 2).sum()/ins_continued_prob_data.shape[0]
        ana_code_logger.info("MSE: %s" % mse)

        rmse = np.sqrt(mse)
        ana_code_logger.info("RMSE: %s" % rmse)

        # 机构维度续报实际结果
        actual_continued_num = df.groupby(self.master_factor)['is_continued'].sum()         # 计算每个机构实际续报人数
        pred_continued_num = df.groupby(self.master_factor)['pred_is_continued'].sum()         # 预测续报人数

        total_student = df.groupby(self.master_factor)[self.slave_factor].count()

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
        ana_code_logger.info("R file path: %s" % filename)

        robjects.r.source(filename)

        # 参数
        self.X_train, self.X_test, self.y_train, self.y_test = self.train_test_dataset()

        model_data = pd.concat([self.X_train, self.y_train], axis=1)
        ana_code_logger.info("R model data shape: %s" % str(model_data.shape))
        ana_code_logger.info("self.X_train.isnull().sum(): %s" % self.X_train.isnull().sum())
        ana_code_logger.info("self.X_train.shape: %s           self.y_train.shape:%s" % (str(self.X_train.shape), str(self.y_train.shape)))

        X_train_r = pandas2ri.py2ri(model_data)
        predictors_vec = robjects.StrVector(self.predictors_vec)

        model_rest = robjects.r.lr_mixed_model(model_data=X_train_r, subject_id=self.master_factor, response=self.y_col,
                                  predictors_vec=predictors_vec, random_intercept=True)

        rest = {}
        for i, name in enumerate(model_rest.names):
            try:
                rest[name] = pandas2ri.ri2py(model_rest[i])
            except:
                rest[name] = model_rest[i]

        ana_code_logger.info("train data ==> model return value: %s" % rest)

        # 合并数据
        ana_code_logger.info(" =============== 合并数据 ========================")
        predicted = rest.get("predicted_probabilities")
        ana_code_logger.info("[预测概率] ====> predicted: %s\n" % predicted.head(20))

        # 改变索引
        end = len(self.X_train.index)
        self.X_train.index = pd.RangeIndex(0, end)

        self.X_train['predicted_probs_without_rand'] = predicted['predicted_probs_without_rand']
        self.X_train['predicted_probs_with_rand'] = predicted['predicted_probs_with_rand']

        ana_code_logger.info("self.X_train.isnull().sum(): %s\n" % self.X_train.isnull().sum())
        ana_code_logger.info("self.X_train[predicted_probs_without_rand].isnull().sum(): %s\n" %
                             self.X_train['predicted_probs_without_rand'].isnull().sum())

        ana_code_logger.info("self.X_train['predicted_probs_without_rand']: %s" %
                             str(self.X_train['predicted_probs_without_rand'].shape))
        ana_code_logger.info("[合并之后的训练集] ===> %s\n" % self.X_train.head(20))

        # 计算模型参数
        ana_code_logger.info(" ========= 计算模型参数 =============== ")

        self.calculate_model_param(self.y_train.to_frame(),
                                   self.X_train['predicted_probs_with_rand'].apply(change).to_frame())

        self.model_rest = rest

    def run_test(self):
        """
        测试集 
        """
        ana_code_logger.info("测试集日志：\n")
        self.X_test = self.deal_data(self.X_test)

        self.X_train['pred_probs'] = self.model_rest.get("predicted_probabilities")['predicted_probs_with_rand']

        ana_code_logger.info("self.X_train.shape: %s       self.X_test.shape:%s " % (str(self.X_train.shape),
                                                                                     str(self.X_test.shape)))

        stu_result = pd.concat([self.X_train[[self.slave_factor, 'pred_probs']],
                                self.X_test[[self.slave_factor, 'pred_probs']]])
        ana_code_logger.info("stu_result.shape: %s" % str(stu_result.shape))

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
            data['pred_probs'] = self.model_rest.get("predicted_probabilities")['predicted_probs_with_rand']
            stu_result = data[[self.slave_factor, 'pred_probs']]
            self.aggregate(stu_result)

    def run(self):
        status = True
        err_msg = log_dir_id = execl_sl = execl_bs = None
        try:
            log_dir_id = self.get_log_path()
            ana_code_logger.info(" ===========训练模型==========")
            self.run_train()

            ana_code_logger.info(" =========== 测试模型==============")
            self.run_test()

            ana_code_logger.info(" ============ 验证模型 =============")
            self.run_validate()

            # 生成输出的df
            train_df_exc = pd.concat([self.X_train, self.y_train], axis=1)
            test_df_exc = pd.concat([self.X_test, self.y_test], axis=1)

            validate_df_exc = self.validate_datasets

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
            ana_code_logger.error("error: %s" % str(exc))
        return log_dir_id, execl_sl, execl_bs, status, err_msg


sk_types = {
    o.sk_type: o for o in globals().values()
    if (
        inspect.isclass(o) and
        issubclass(o, BaseSkModel) and
        o.sk_type not in config.get('VIZ_TYPE_BLACKLIST'))}
