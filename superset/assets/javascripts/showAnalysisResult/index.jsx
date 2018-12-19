import React from 'react';
import ReactDOM from 'react-dom';
import {appSetup} from "../common";
import {initJQueryAjax} from "../modules/utils";



appSetup();  // 加载ajax
initJQueryAjax(); // 设置token

const analysisViewContainer = document.getElementById('app');
const bootstrapData = JSON.parse(analysisViewContainer.getAttribute('data-bootstrap'));

ReactDOM.render(
    <div>
      <Showresult data={bootstrapData.form_data.model_result_execl_bs}/>
    </div>,
  analysisViewContainer,
);