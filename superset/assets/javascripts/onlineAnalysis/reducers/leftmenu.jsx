
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
    WATCH_DESCRIBE,
    WATCH_CORR
} from "../constants/leftmenu";

const leftmenu = (state = {}, action = {}) => {
  switch(action.type) {
      case GET_ALLMODEL:
        const slice = Object.assign({},state.slice);
        const all_model = Object.assign({},slice,{all_model:action.res.data});
        return Object.assign({}, state, {slice:all_model});

      case SET_MODEL:
        const form_data = Object.assign({},state.form_data);
        const new_form_data = Object.assign({},form_data,{sk_type:action.model_name});
        console.log(Object.assign({}, state,{form_data:new_form_data}));
        return Object.assign({}, state,{form_data:new_form_data});

      case GET_ALL_VERSION:
        const form_data_verison = Object.assign({},state.form_data);
        const verison_form_data = Object.assign({},form_data_verison,{versions:action.res.data});
        console.log(Object.assign({}, state, {form_data: verison_form_data}));
        return Object.assign({}, state, {form_data: verison_form_data});

      case GET_ALL_DATASOURCE:
        const slice_datasource = Object.assign({},state.slice);
        const all_datasource = Object.assign({}, slice_datasource, { all_datasource: action.res.data });
        return Object.assign({}, state, {slice:all_datasource});

      case GET_DATASOURCE_COLUMNS:
        const slice_datasource_columns = Object.assign({},state.slice);
        const all_datasource_columns = Object.assign({}, slice_datasource_columns, {all_datasource_columns: action.res.data});
        return Object.assign({}, state, {slice: all_datasource_columns});

      case MODIFY_DATASOURCE:
          const datasource = action.id + "__table" ;
          const new_datasource = Object.assign({},state.form_data,{datasource:datasource});
          const new_form = Object.assign({},state,{form_data:new_datasource});
          const new_state = Object.assign({},state,new_form);
          return Object.assign({},new_state,{datasource_id:action.id, datasource_name:action.name});
      //
      // case GET_CODE:
      //     return Object.assign({},state,{code: action.res.data.code});

      case GET_DEAINA:
          return Object.assign({},state,{all_dealina: action.res});

      case SET_DESCRIPTION_IMG:
          const set_description_img = Object.assign({},state.form_data,{ description_img:{ url: action.url, name:action.name} });
          return Object.assign({}, state, {form_data: set_description_img});

      case SET_NULL_OPERATION:
          const set_null_operation = Object.assign({},state.form_data.null_operate,{operate:action.operate,detail:action.detail});
          // console.log('yyy',Object.assign({},state,set_null_operation));
          const new_null_form = Object.assign({},state.form_data,{null_operate:set_null_operation});
          console.log('zzz',new_null_form);
          console.log(Object.assign({},state,{form_data:new_null_form}));
          return Object.assign({},state,{form_data:new_null_form});

      case NEW_VARIABLE_BOX:
          const new_variable_box = Object.assign({},state.form_data,{variable_box: state.form_data.variable_box.concat({field:'',bins:'',labels:''})});
          console.log('new_var',new_variable_box);
          console.log('new_state',Object.assign({},state,{form_data:new_variable_box}));
          return Object.assign({},state,{form_data:new_variable_box});

      case DELETE_VARIABLE_BOX:
          const old_variable_box = state.form_data.variable_box;
          old_variable_box.splice(action.index,1);
          // console.log(state);
          // return state;
          // console.log('after',afterdetele);
          const after_variable_box = Object.assign({},state.form_data,{variable_box:old_variable_box});
          // console.log('after',Object.assign({},state,{form_data:after_variable_box}));
          return Object.assign({},state,{form_data:after_variable_box});

      case MODIFY_VARIABLE_BOX_FIELD:
          state.form_data.variable_box[action.index].field = action.name;
          // console.log(333,modify_name);
          console.log(333,state);
          return Object.assign({},state);

      case MODIFY_VARIABLE_BOX_BINS:
          state.form_data.variable_box[action.index].bins = action.bins;
          console.log(333,state);
          return Object.assign({},state);

      case MODIFY_VARIABLE_BOX_LABELS:
          state.form_data.variable_box[action.index].labels = action.labels;
          console.log(333,state);
          return Object.assign({},state);

      case INCREAMENT_DUMMY:
          const new_dummy = Object.assign({},state.form_data,{dummy_variable: state.form_data.dummy_variable.concat({field:'',labels:''})});
          console.log('new_var',new_dummy);
          console.log('new_state',Object.assign({},state,{form_data:new_dummy}));
          return Object.assign({},state,{form_data:new_dummy});

      case MODIFY_DUMMY_FIELD:
          state.form_data.dummy_variable[action.index].field = action.field;
          // console.log(333,modify_name);

          console.log(333,state);
          return Object.assign({},state);

      case MODIFY_DUMMY_VALUE:
          state.form_data.dummy_variable[action.index].labels = action.value;
          console.log('MODIFY_DUMMY_VALUE' ,state);
          return Object.assign({},state);

      case DELETE_DUMMY:
          const old_dummy = state.form_data.dummy_variable;
          old_dummy.splice(action.index,1);
          console.log(old_dummy);
          // console.log(state);
          // return state;
          // console.log('after',afterdetele);
          const after_dummy = Object.assign({},state.form_data,{dummy_variable:old_dummy});
          console.log('after',Object.assign({},state,{form_data:after_dummy}));
          return Object.assign({},state,{form_data:after_dummy});

      case INCREAMENT_CORRELATION:
          const increament = state.form_data.correlation_analysis;
          increament.push([0,0,0]);
          console.log(111,state);
          return Object.assign({},state);

      case DELETE_CORRELATION:
          const old_corr = state.form_data.correlation_analysis;
          old_corr.splice(action.index,1);
          const after_corr = Object.assign({},state.form_data,{correlation_analysis:old_corr});
          // console.log('after',Object.assign({},state,{form_data:after_variable_box}));
          return Object.assign({},state,{form_data:after_corr});

      case MODIFY_CORRELATION_FIELD:
          state.form_data.correlation_analysis[action.index][0] = action.field;
          console.log('field' ,state);
          return Object.assign({},state);


      case MODIFY_CORRELATION_TWO:
          state.form_data.correlation_analysis[action.index][1] = action.two;
          console.log('TWO' ,state);
          return Object.assign({},state);

      case MODIFY_CORRELATION_LAST:
          state.form_data.correlation_analysis[action.index][2] = action.last;
          console.log('LAST' ,state);
          return Object.assign({},state);

      case ADD_TRAIN:
          const add_train = Object.assign({},state.form_data,{train_dataset: state.form_data.train_dataset.concat({col:'',op:'',val:''})});
          return Object.assign({},state,{form_data:add_train});

      case DELETE_TRAIN:
          const old_filters = state.form_data.train_dataset;
          old_filters.splice(action.index,1);
          return Object.assign({},state);

      case MODIFY_TRAIN_COL:
          state.form_data.train_dataset[action.index].col = action.res;
          console.log(state);
          return Object.assign({},state);

      case MODIFY_TRAIN_OP:
          state.form_data.train_dataset[action.index].op = action.res;
          console.log(state);
          return Object.assign({},state);

      case MODIFY_TRAIN_VAL:
          state.form_data.train_dataset[action.index].val = action.res;
          console.log(state);
          return Object.assign({},state);

      case ADD_VALIDATE_DATASETS:
          const add_val = Object.assign({},state.form_data,{validate_datasets: state.form_data.validate_datasets.concat({name:'',filters:[]})});
          return Object.assign({},state,{form_data:add_val});

      case ADD_VALIDATE_FILTERS:
          state.form_data.validate_datasets[action.index].filters.push({col:'',op:'',val:''});
          return Object.assign({},state);

      case DELETE_VALIDATE_DATASETS:
          const old_val = state.form_data.validate_datasets;
          old_val.splice(action.index,1);
          const after_val = Object.assign({},state.form_data,{correlation_analysis:old_val});
          console.log(Object.assign({},state,{form_data:after_val}));
          return Object.assign({},state,{form_data:after_val});

      case MODIFY_VAL_NAME:
          state.form_data.validate_datasets[action.index].name = action.res;
          console.log(state);
          return Object.assign({},state);

      case DELETE_VALIDATE_FILTERS:
            const old_vali = state.form_data.validate_datasets[action.val_index].filters;
            old_vali.splice(action.filter_index,1);
            console.log(old_vali);
            console.log(state);
            return Object.assign({},state);

      case MODIFT_VALIDATE_FILTERS_COL:
          state.form_data.validate_datasets[action.val_index].filters[action.filter_index].col=action.res;
          console.log(state);
          return Object.assign({},state);

      case MODIFT_VALIDATE_FILTERS_OP:
          state.form_data.validate_datasets[action.val_index].filters[action.filter_index].op=action.res;
          console.log(state);
          return Object.assign({},state);

      case MODIFT_VALIDATE_FILTERS_VAL:
          console.log(state);
          state.form_data.validate_datasets[action.val_index].filters[action.filter_index].val =action.res;
          console.log(state);
          return Object.assign({},state);

      case GET_MODEL_PARAMETER:
          console.log('res',action.res);
          const model_param = Object.assign({},state.form_data,{model_param:action.res.data});
          console.log(model_param);
          // console.log(111111,Object({},state,{form_data:model_param}));
          return Object.assign({},state,{form_data:model_param});

      case MODIFY_PARAMETER:
          state.form_data.model_param[action.name][action.filter_name] = action.value;
          return Object.assign({},state);

      case RUN:
          console.log(action.data);
          return state;




    default: return state;
  }
};

export default leftmenu;