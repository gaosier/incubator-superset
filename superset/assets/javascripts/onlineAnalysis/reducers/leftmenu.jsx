import {
    GET_ALLMODEL,
    SET_MODEL,
    GET_ALL_VERSION,
    GET_ALL_DATASOURCE,
    GET_DATASOURCE_COLUMNS,
    GET_MODEL_PARAMETER,
    MODIFY_DATASOURCE,
    SET_DESCRIPTION_IMG,
    GET_DEAINA,
    SET_NULL_OPERATION,
    NEW_VARIABLE_BOX,
    DELETE_VARIABLE_BOX,
    MODIFY_VARIABLE_BOX_FIELD,
    MODIFY_VARIABLE_BOX_BINS,
    MODIFY_VARIABLE_BOX_LABELS,
    MODIFY_INCLUDE_ENDPOINT,
    INCREAMENT_DUMMY,
    MODIFY_DUMMY_FIELD,
    MODIFY_DUMMY_VALUE,
    DELETE_DUMMY,
    INCREAMENT_CORRELATION,
    DELETE_CORRELATION,
    MODIFY_CORRELATION_TWO,
    MODIFY_CORRELATION_LAST,
    MODIFY_CORRELATION_FIELD,
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
    WATCH_DESCRIBE,
    WATCH_CORR,
    SET_NAME,
    SET_VERSION,
    LOG,
    SET_RUN,
    CHOICE_VERSION, DELETE_IMG
} from "../constants/leftmenu";

const leftmenu = (state = {}, action = {}) => {
    switch (action.type) {
        case GET_ALLMODEL:
            const slice = Object.assign({}, state.slice);
            const all_model = Object.assign({}, slice, {all_model: action.res.data});
            return Object.assign({}, state, {slice: all_model});

        case SET_MODEL:
            const form_data = Object.assign({}, state.form_data);
            const new_form_data = Object.assign({}, form_data, {sk_type: action.model_name});
            return Object.assign({}, state, {form_data: new_form_data});

        case GET_ALL_VERSION:
            const slice_version = Object.assign({}, state.slice, {all_version: action.res.data});
            return Object.assign({}, state, {slice: slice_version});

        case GET_ALL_DATASOURCE:
            const slice_datasource = Object.assign({}, state.slice);
            const all_datasource = Object.assign({}, slice_datasource, {all_datasource: action.res.data});
            return Object.assign({}, state, {slice: all_datasource});

        case GET_DATASOURCE_COLUMNS:
            const slice_datasource_columns = Object.assign({}, state.slice);
            const all_datasource_columns = Object.assign({}, slice_datasource_columns, {all_datasource_columns: action.res.data});
            return Object.assign({}, state, {slice: all_datasource_columns});

        case MODIFY_DATASOURCE:
            const new_state = Object.assign({}, state, {form_data: action.form_data});
            return Object.assign({}, new_state, {
                datasource_id: action.id,
                datasource_name: action.name,
                run_load: false
            });

        case GET_DEAINA:
            return Object.assign({}, state, {all_dealina: action.res});

        case SET_DESCRIPTION_IMG:
            const set_description_img = Object.assign({}, state.form_data, {description_img: action.name});
            return Object.assign({}, state, {form_data: set_description_img});

        case SET_NULL_OPERATION:
            const set_null_operation = Object.assign({}, state.form_data.null_operate, {
                operate: action.operate,
                detail: action.detail
            });
            const new_null_form = Object.assign({}, state.form_data, {null_operate: set_null_operation});
            return Object.assign({}, state, {form_data: new_null_form});

        case NEW_VARIABLE_BOX:
            const new_variable_box = Object.assign({}, state.form_data, {
                variable_box: state.form_data.variable_box.concat({
                    field: '',
                    bins: '',
                    labels: '',
                    right: false,
                    left: false
                })
            });
            return Object.assign({}, state, {form_data: new_variable_box});

        case DELETE_VARIABLE_BOX:
            const old_variable_box = state.form_data.variable_box;
            old_variable_box.splice(action.index, 1);
            const after_variable_box = Object.assign({}, state.form_data, {variable_box: old_variable_box});
            return Object.assign({}, state, {form_data: after_variable_box});

        case MODIFY_VARIABLE_BOX_FIELD:
            state.form_data.variable_box[action.index].field = action.name;
            return Object.assign({}, state);

        case MODIFY_VARIABLE_BOX_BINS:
            state.form_data.variable_box[action.index].bins = action.bins;
            return Object.assign({}, state);

        case MODIFY_INCLUDE_ENDPOINT:
            state.form_data.variable_box[action.index][action.res] = action.value;
            return Object.assign({}, state);

        case MODIFY_VARIABLE_BOX_LABELS:
            state.form_data.variable_box[action.index].labels = action.labels;
            return Object.assign({}, state);

        case INCREAMENT_DUMMY:
            const new_dummy = Object.assign({}, state.form_data, {
                dummy_variable: state.form_data.dummy_variable.concat({
                    field: '',
                    labels: ''
                })
            });
            return Object.assign({}, state, {form_data: new_dummy});

        case MODIFY_DUMMY_FIELD:
            state.form_data.dummy_variable[action.index].field = action.field;
            return Object.assign({}, state);

        case MODIFY_DUMMY_VALUE:
            state.form_data.dummy_variable[action.index].labels = action.value;
            return Object.assign({}, state);

        case DELETE_DUMMY:
            const old_dummy = state.form_data.dummy_variable;
            old_dummy.splice(action.index, 1);
            const after_dummy = Object.assign({}, state.form_data, {dummy_variable: old_dummy});
            return Object.assign({}, state, {form_data: after_dummy});

        case INCREAMENT_CORRELATION:
            const increament = state.form_data.correlation_analysis;
            increament.push([0, 0, 0]);
            return Object.assign({}, state);

        case DELETE_CORRELATION:
            const old_corr = state.form_data.correlation_analysis;
            old_corr.splice(action.index, 1);
            const after_corr = Object.assign({}, state.form_data, {correlation_analysis: old_corr});
            return Object.assign({}, state, {form_data: after_corr});

        case MODIFY_CORRELATION_FIELD:
            state.form_data.correlation_analysis[action.index][0] = action.field;
            return Object.assign({}, state);


        case MODIFY_CORRELATION_TWO:
            state.form_data.correlation_analysis[action.index][1] = action.two;
            return Object.assign({}, state);

        case MODIFY_CORRELATION_LAST:
            state.form_data.correlation_analysis[action.index][2] = action.last;
            return Object.assign({}, state);

        case ADD_TRAIN:
            const add_train = Object.assign({}, state.form_data, {
                train_dataset: state.form_data.train_dataset.concat({
                    col: '',
                    op: '',
                    val: ''
                })
            });
            return Object.assign({}, state, {form_data: add_train});

        case DELETE_TRAIN:
            const old_filters = state.form_data.train_dataset;
            old_filters.splice(action.index, 1);
            return Object.assign({}, state);

        case MODIFY_TRAIN_COL:
            state.form_data.train_dataset[action.index].col = action.res;
            state.form_data.train_dataset[action.index].val = '';
            return Object.assign({}, state);

        case MODIFY_TRAIN_OP:
            state.form_data.train_dataset[action.index].op = action.res;
            return Object.assign({}, state);

        case MODIFY_TRAIN_VAL:
            state.form_data.train_dataset[action.index].val = action.res;
            return Object.assign({}, state);

        case ADD_VALIDATE_DATASETS:
            const add_val = Object.assign({}, state.form_data, {
                validate_datasets: state.form_data.validate_datasets.concat({
                    name: '',
                    filters: []
                })
            });
            return Object.assign({}, state, {form_data: add_val});

        case ADD_VALIDATE_FILTERS:
            state.form_data.validate_datasets[action.index].filters.push({col: '', op: '', val: ''});
            return Object.assign({}, state);

        case DELETE_VALIDATE_DATASETS:
            const old_val = state.form_data.validate_datasets;
            old_val.splice(action.index, 1);
            const after_val = Object.assign({}, state.form_data, {correlation_analysis: old_val});
            return Object.assign({}, state, {form_data: after_val});

        case MODIFY_VAL_NAME:
            state.form_data.validate_datasets[action.index].name = action.res;
            return Object.assign({}, state);

        case DELETE_VALIDATE_FILTERS:
            const old_vali = state.form_data.validate_datasets[action.val_index].filters;
            old_vali.splice(action.filter_index, 1);
            return Object.assign({}, state);

        case MODIFT_VALIDATE_FILTERS_COL:
            state.form_data.validate_datasets[action.val_index].filters[action.filter_index].col = action.res;
            state.form_data.validate_datasets[action.val_index].filters[action.filter_index].val = '';
            return Object.assign({}, state);

        case MODIFT_VALIDATE_FILTERS_OP:
            state.form_data.validate_datasets[action.val_index].filters[action.filter_index].op = action.res;
            return Object.assign({}, state);

        case MODIFT_VALIDATE_FILTERS_VAL:
            state.form_data.validate_datasets[action.val_index].filters[action.filter_index].val = action.res;
            return Object.assign({}, state);

        case GET_MODEL_PARAMETER:
            const model_param = Object.assign({}, state.form_data, {model_param: action.res.data});
            return Object.assign({}, state, {form_data: model_param});

        case MODIFY_PARAMETER:
            state.form_data.model_param[action.name][action.filter_name] = action.value;
            return Object.assign({}, state);

        case RUN:
            state.form_data.log_dir_id = action.data.log_dir_id;
            state.form_data.model_result_execl_sl = action.data.model_result_execl_sl;
            state.form_data.model_result_execl_bs = action.data.model_result_execl_bs;
            return Object.assign({}, state, {run_load: false, run_finish: true});

        case GET_ALL_FILTER_COLUMNS:
            const get_all_column = Object.assign({}, state.slice, {all_select_column: action.res.data});
            return Object.assign({}, state, {slice: get_all_column});

        case SET_NAME:
            const set_name = Object.assign({}, state.form_data, {analysis_name: action.name});
            return Object.assign({}, state, {form_data: set_name});

        case SET_VERSION:
            const set_version = Object.assign({}, state.form_data, {version: action.name});
            return Object.assign({}, state, {form_data: set_version});

        case WATCH_CORR:
            const set_corr_img = Object.assign({}, state.form_data, {correlation_analysis_image: action.data.name});
            return Object.assign({}, state, {form_data: set_corr_img});

        case SET_RUN:
            return Object.assign({}, state, {run_load: true});

        case CHOICE_VERSION:
            action.now_version.version = action.res;
            return Object.assign({}, state, {form_data: action.now_version, run_load: false});

        case DELETE_IMG:
            const delete_img = Object.assign({}, state.form_data, {correlation_analysis_image: ''});
            return Object.assign({}, state, {form_data: delete_img});

        default:
            return state;
    }
};

export default leftmenu;