import axios from 'axios';
import {notification} from 'antd';
import {
    GET_ALLMODEL,
    SET_MODEL,
    GET_ALL_VERSION,
    GET_ALL_DATASOURCE,
    GET_DATASOURCE_COLUMNS,
    GET_MODEL_PARAMETER, GET_DEAINA,
    MODIFY_DATASOURCE,
    SET_DESCRIPTION_IMG,
    SET_NULL_OPERATION,
    NEW_VARIABLE_BOX,
    MODIFY_VARIABLE_BOX_FIELD,
    MODIFY_VARIABLE_BOX_BINS,
    MODIFY_VARIABLE_BOX_LABELS,
    DELETE_VARIABLE_BOX,
    INCREAMENT_DUMMY,
    MODIFY_DUMMY_FIELD,
    MODIFY_DUMMY_VALUE,
    DELETE_DUMMY,
    INCREAMENT_CORRELATION,
    MODIFY_CORRELATION_FIELD,
    MODIFY_CORRELATION_TWO,
    MODIFY_CORRELATION_LAST,
    DELETE_CORRELATION,
    WATCH_DESCRIBE,
    WATCH_CORR,
    ADD_TRAIN,
    DELETE_TRAIN,
    MODIFY_TRAIN_COL,
    MODIFY_TRAIN_OP,
    MODIFY_TRAIN_VAL,
    ADD_VALIDATE_DATASETS,
    DELETE_VALIDATE_DATASETS,
    ADD_VALIDATE_FILTERS,
    MODIFY_VAL_NAME,
    DELETE_VALIDATE_FILTERS,
    MODIFT_VALIDATE_FILTERS_COL,
    MODIFT_VALIDATE_FILTERS_OP,
    MODIFT_VALIDATE_FILTERS_VAL,
    MODIFY_PARAMETER,
    RUN,
    GET_ALL_FILTER_COLUMNS,
    SET_NAME,
    SET_VERSION,
    CHOICE_VERSION,
    LOG,
    QUERY_RUN,
    SET_RUN,
    MODIFY_INCLUDE_ENDPOINT
} from "../constants/leftmenu";
import {get_log} from '../actions/rightinfo';

// 获取所有模型名
export const get_all_model = () => {
    return dispatch => {
        axios.get("/online/skmodels/")
            .then(res => {
                dispatch(get_allmodel(res));
            })
            .catch(error => {
                notification['error']({
                    message: '获取模型名失败',
                    description: '详情请咨询相关人员.',
                });
            })
    }
};

export const get_allmodel = (res) => {
    return {
        type: GET_ALLMODEL,
        res
    }
};

//获取所有的可过滤的表字段
export const get_all_filter_column = (id) => {
    return dispatch => {
        axios.get("/online/columns/table/" + id + "/")
            .then(res => {
                dispatch(get_all_columns(res));
            })
            .catch(error => {
                notification['error']({
                    message: '获取表字段失败',
                    description: '详情请咨询相关人员.',
                });
            })
    }
};

export const get_all_columns = (res) => {
    return {
        type: GET_ALL_FILTER_COLUMNS,
        res
    }
};

// 设置选择的模型名
export const set_model = (model_name) => {
    return {
        type: SET_MODEL,
        model_name
    }
};

// 获取所有的版本号
export const get_all_version = (modal_name) => {
    return dispatch => {
        axios.get('/online/versions/' + modal_name + '/')
            .then(res => {
                dispatch(get_allversion(res));
            })
            .catch(error => {
                notification['error']({
                    message: '获取版本号失败',
                    description: '详情请咨询相关人员.',
                });
            })
    }
};

export const get_allversion = (res) => {
    return {
        type: GET_ALL_VERSION,
        res
    }
};

// 获取所有的表名
export const get_all_datasource = () => {
    return dispatch => {
        axios.get('/online/datasources/')
            .then(res => {
                dispatch(get_alldatasource(res));
            })
            .catch(error => {
                notification['error']({
                    message: '获取所有表名失败',
                    description: '详情请咨询相关人员.',
                });
            })
    }
};

export const get_alldatasource = (res) => {
    return {
        type: GET_ALL_DATASOURCE,
        res
    }
};

// 修改表名和id
export const modify_datasource = (id, name) => {
    const datasource = id + '__table';
    const form_data = {
            datasource: datasource,
            version: '',
            sk_type:  '',
            analysis_id:  '',
            name: '',
            null_operate: {
                operate: '',
                detail: []
            },
            variable_box:  [],
            dummy_variable:  [],
            correlation_analysis: [],
            train_dataset: [],
            validate_datasets: [],
            model_param: [],
            description_img: "",
            log_dir_id: "",
            correlation_analysis_image: "",
            model_result_execl_sl:  "",
            model_result_execl_bs:""
        };
    return {
        type: MODIFY_DATASOURCE,
        id,
        name,
        form_data
    }
};

// 获取所有的列名
export const get_datasource_columns = (id) => {
    return dispatch => {
        axios.get('/online/table/schema/table/' + id + '/')
            .then(res => {
                dispatch(get_datasourcecolumns(res));
            })
            .catch(error => {
                notification['error']({
                    message: '获取列名失败',
                    description: '详情请咨询相关人员.',
                });
            })
    }
};

export const get_datasourcecolumns = (res) => {
    return {
        type: GET_DATASOURCE_COLUMNS,
        res
    }
};


// 获取机器学习模型参数
export const get_model_parameter = (name) => {
    return dispatch => {
        axios.get("/online/model/params/" + name + '/')
            .then(res => {
                dispatch(get_modelparameter(res))
            })
            .catch(error => {
                console.log(error);
                notification['error']({
                    message: '获取机器学习模型参数失败',
                    description: '获取机器学习模型参数失败,详情请咨询相关人员.',
                });
            })
    }
};

export const get_modelparameter = (res) => {
    return {
        type: GET_MODEL_PARAMETER,
        res
    }
};

//改变机器学习模型参数
export const modify_parameter = (name, filter_name, value) => {
    return {
        type: MODIFY_PARAMETER,
        name,
        filter_name,
        value
    }
};

// 获取所有的缺失值
export const get_all_dealna = (sk_type, id) => {
    const form_data = {sk_type: sk_type, datasource: id + "__table"};
    return dispatch => {
        $.ajax({
            type: 'POST',
            url: "/online/dealna/",
            data: {
                form_data: JSON.stringify(form_data),
            },
            success: ((data) => {
                dispatch(get_alldealna(data))
            }),
            error: ((data, type, err) => {
                console.log(data, type, err);
                notification['error']({
                    message: '获取缺失值失败',
                    description: '获取缺失值必须选择模型名称,您可能未选择模型名,若您已选择,请咨询相关人员.',
                });
            }),
        })
    }
};

export const get_alldealna = (res) => {
    return {
        type: GET_DEAINA,
        res
    }
};

//设置描述分析图片

export const set_description_img = (name) => {
    return {
        type: SET_DESCRIPTION_IMG,
        name
    }
};

// 保存空值处理方式

export const set_null_operation = (operate, detail) => {
    return {
        type: SET_NULL_OPERATION,
        operate,
        detail
    }
};

// 增加新的变量分箱条件

export const set_variable_box = () => {
    return {
        type: NEW_VARIABLE_BOX,
    }
};

// 修改分箱条件中的列名

export const modify_variable_box_field = (index, name) => {
    return {
        type: MODIFY_VARIABLE_BOX_FIELD,
        index,
        name
    }
};

// 修改分箱条件中的区间

export const modify_variable_box_bins = (index, bins) => {
    return {
        type: MODIFY_VARIABLE_BOX_BINS,
        index,
        bins
    }
};

// 修改是否包含左右端点
export const modify_include_endpoint = (index,value,res) =>{
    return {
        type:MODIFY_INCLUDE_ENDPOINT,
        index,
        value,
        res
    }
};

// 修改分箱条件中的代替值

export const modify_variable_box_labels = (index, labels) => {
    return {
        type: MODIFY_VARIABLE_BOX_LABELS,
        index,
        labels
    }
};

// 删除分箱条件

export const delete_variable_box = (index) => {
    return {
        type: DELETE_VARIABLE_BOX,
        index
    }
};

// 增加哑变量处理条件

export const increase_dummy = () => {
    return {
        type: INCREAMENT_DUMMY
    }
};

// 修改哑变量处理的列名

export const modify_dummy_field = (index, field) => {
    return {
        type: MODIFY_DUMMY_FIELD,
        index,
        field
    }
};

// 修改哑变量处理的值

export const modify_dummy_value = (index, value) => {
    return {
        type: MODIFY_DUMMY_VALUE,
        index,
        value
    }
};

// 删除哑变量处理条件

export const delete_dummy = (index) => {
    return {
        type: DELETE_DUMMY,
        index
    }
};

// 增加变量相关性分析

export const increament_correlation = () => {
    return {
        type: INCREAMENT_CORRELATION
    }

};

// 修改变量相关性的列

export const modify_correlation_field = (index, field) => {
    return {
        type: MODIFY_CORRELATION_FIELD,
        index,
        field
    }
};

// 修改变量相关性的第二个参数

export const modify_correlation_two = (index, two) => {
    return {
        type: MODIFY_CORRELATION_TWO,
        index,
        two
    }
};

// 修改变量相关性的最后一个参数

export const modify_correlation_last = (index, last) => {
    return {
        type: MODIFY_CORRELATION_LAST,
        index,
        last
    }
};

// 删除变量相关性分析条件

export const delete_correlation = (index) => {
    return {
        type: DELETE_CORRELATION,
        index
    }
};

// 查看数据分布

export const watch_describe = (null_operate) => {
    return dispatch => {
        $.ajax({
            type: 'POST',
            url: "/online/describe/",
            data: {
                form_data: JSON.stringify(null_operate),
            },
            success: ((data) => {
                dispatch(see_describe(data))
            }),
            error: (() => {
                notification['error']({
                    message: '查看数据分布失败',
                    description: '详情请咨询相关人员.',
                });
            }),
        })
    }
};

export const see_describe = (data) => {
    return {
        type: WATCH_DESCRIBE,
        data
    }
};

// 查看变量相关性

export const watch_corr = (null_operate, datasource, sk_type) => {
    const corr = {correlation_analysis: null_operate, sk_type: sk_type, datasource: datasource};
    return dispatch => {
        $.ajax({
            type: 'POST',
            url: "/online/correlation_analysis/",
            data: {
                form_data: JSON.stringify(corr),
            },
            success: ((data) => {
                dispatch(see_corr(data))
            }),
            error: (() => {
                notification['error']({
                    message: '查看变量相关性失败',
                    description: '详情请咨询相关人员.',
                });
            }),
        })
    }
};

export const see_corr = (data) => {
    return {
        type: WATCH_CORR,
        data
    }
};


// 增加跑模型数据集

export const add_train_dataset = () => {
    return {
        type: ADD_TRAIN
    }
};

// 删除跑模型数据集

export const delete_train_dataset = (index) => {
    return {
        type: DELETE_TRAIN,
        index
    }
};

// 修改跑模型数据集中的列名

export const modify_train_col = (index, res) => {
    return {
        type: MODIFY_TRAIN_COL,
        index,
        res
    }
};

// 修改跑模型数据集中的运算符

export const modify_train_op = (index, res) => {
    return {
        type: MODIFY_TRAIN_OP,
        index,
        res
    }
};

// 修改跑模型数据集中的值

export const modify_train_val = (index, res) => {
    return {
        type: MODIFY_TRAIN_VAL,
        index,
        res
    }
};

// 增加验证数据集

export const add_validate_datasets = () => {
    return {
        type: ADD_VALIDATE_DATASETS
    }
};

// 增加验证数据集中的过滤条件

export const add_val_filter = (index) => {
    return {
        type: ADD_VALIDATE_FILTERS,
        index
    }
};

// 删除验证数据集

export const delete_validate_datasets = (index) => {
    return {
        type: DELETE_VALIDATE_DATASETS,
        index
    }
};

// 修改验证数据集名称

export const modify_name = (index, res) => {
    return {
        type: MODIFY_VAL_NAME,
        index,
        res
    }
};

// 删除验证数据集中的过滤条件

export const delete_vali_filters = (val_index, filter_index) => {
    return {
        type: DELETE_VALIDATE_FILTERS,
        val_index,
        filter_index
    }
};

// 修改验证数据集中过滤条件的列

export const modify_filter_col = (val_index, filter_index, res) => {
    return {
        type: MODIFT_VALIDATE_FILTERS_COL,
        val_index,
        filter_index,
        res
    }
};

// 修改验证数据集中过滤条件的判断符

export const modify_filter_op = (val_index, filter_index, res) => {
    return {
        type: MODIFT_VALIDATE_FILTERS_OP,
        val_index,
        filter_index,
        res
    }
};

// 修改验证数据集中过滤条件的值

export const modify_filter_val = (val_index, filter_index, res) => {
    return {
        type: MODIFT_VALIDATE_FILTERS_VAL,
        val_index,
        filter_index,
        res
    }
};

// 开始跑模型
export const query_run = () => {
    return {
        type: QUERY_RUN
    }
};

// 跑模型

export const run_model = (form_data) => {
    return dispatch => {
        $.ajax({
            type: 'POST',
            url: "/online/run/model/",
            data: {
                form_data: JSON.stringify(form_data),
            },
            success: ((data) => {
                dispatch(run_models(data));

            }),
            error: ((data, type, err) => {
                console.log(data, type, err);
                notification['error']({
                    message: '跑模型失败',
                    description: '详情请咨询相关人员.',
                });
            }),
        })
    }
};

export const run_models = (data) => {
    return {
        type: RUN,
        data
    }
};

// 设置分析模型名称

export const set_name = (name) => {
    return {
        type: SET_NAME,
        name
    }
};

// 设置分析模型版本名称

export const set_version = (name) => {
    return {
        type: SET_VERSION,
        name
    }
};

// 保存模型

export const save_allmodal = (form_data, id, action, name, version) => {
    delete form_data.version;
    delete form_data.analysis_name;
    return dispatch => {
        $.ajax({
            type: 'POST',
            url: "/online/analysis/table/" + id + '/?action=' + action + '&name=' + name + '&version=' + version,
            data: {
                form_data: JSON.stringify(form_data),
            },
            success: ((data) => {
                console.log(data);
                dispatch(save_all_model(data))
            }),
            error: ((data, type, err) => {
                console.log(data, type, err);
                notification['error']({
                    message: '保存模型失败',
                    description: '详情请咨询相关人员.',
                });
            }),
        })
    }
};

export const save_all_model = (data) => {
    return {
        type: "aaa",
        data
    }
};

// 设置版本号

export const choice_version = (res,all_version) => {
    const now_version = JSON.parse(all_version[res]);
    console.log(now_version);
    return {
        type: CHOICE_VERSION,
        res,
        now_version
    }
};

// 设置正在跑模型标识

export const set_run = () =>{
    return {
        type:SET_RUN
    }
};