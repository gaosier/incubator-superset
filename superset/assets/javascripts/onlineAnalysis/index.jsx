import React from 'react';
import ReactDOM from 'react-dom';
import { createStore, applyMiddleware, compose } from 'redux';
import { Provider } from 'react-redux';
import thunk from 'redux-thunk';

import { appSetup } from '../common';
import './main.css';
import '../../stylesheets/reactable-pagination.css';
import {initJQueryAjax, initAixos} from "../modules/utils";
import rootReducer from "../onlineAnalysis/reducers";
import {initEnhancer} from "../reduxUtils";
import Analysis from './components/Analysis';
// import AlertsWrapper from '../components/AlertsWrapper';


appSetup();  // 加载ajax
initJQueryAjax(); // 设置token

const analysisViewContainer = document.getElementById('app');
const bootstrapData = JSON.parse(analysisViewContainer.getAttribute('data-bootstrap'));


const  initState = {
    leftmenu: {
        form_data:{
            datasource:bootstrapData.form_data.datasource || "158__table",
            version: bootstrapData.form_data.version || '',
            sk_type: bootstrapData.form_data.sk_type || '',
            analysis_id: bootstrapData.form_data.analysis_id || '',
            analysis_name: bootstrapData.form_data.analysis_name || '',
            null_operate: bootstrapData.form_data.null_operate || {
                operate: '',
                detail:[]
            },
            variable_box: bootstrapData.form_data.variable_box || [],
            dummy_variable: bootstrapData.form_data.dummy_variable || [],
            correlation_analysis: bootstrapData.form_data.correlation_analysis || [],
            train_dataset: bootstrapData.form_data.train_dataset || [],
            validate_datasets: bootstrapData.form_data.validate_datasets || [],
            model_param: bootstrapData.form_data.model_param || [],
            description_img: bootstrapData.form_data.description_img || {
                url:null,
                name:null
            },
            log_dir_id: bootstrapData.form_data.log_dir_id || "",
            correlation_analysis_image:  bootstrapData.form_data.correlation_analysis_image || "",
            model_result_execl_sl: bootstrapData.form_data.model_result_execl_sl || "",
            model_result_execl_bs: bootstrapData.form_data.model_result_execl_bs || ""
        },
        slice:{
            all_datasource:[],
            all_model:[],
            all_version:[],
            all_filter:[],
            all_datasource_columns:{
                columns:[],
                metrics:[]
            },
            all_choice_column:[]
        },
        datasource_name: bootstrapData.datasource_name || '',
        datasource_id: bootstrapData.datasource_id || 0,
        datasource_type: bootstrapData.datasource_type || 'table',
        user_id: bootstrapData.user_id || '0',
        can_add: bootstrapData.can_add || true,
        can_overwrite: bootstrapData.can_overwrite || null,
        all_dealina:{}

    },
    rightinfo:{
        log:[],
        image:[],
        show:[]
    }
};

const store = createStore(rootReducer, initState,
  compose(applyMiddleware(thunk), initEnhancer(false)),
);

ReactDOM.render(
  <Provider store={store}>
    <div>
      <Analysis />
      {/*<AlertsWrapper initMessages={bootstrappedState.common.flash_messages} />*/}
    </div>
  </Provider>,
  analysisViewContainer,
);