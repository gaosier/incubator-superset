import React from 'react';
import ReactDOM from 'react-dom';
import {appSetup} from "../common";
import {initJQueryAjax} from "../modules/utils";
import ShowResult  from './ShowResult';
import '../../stylesheets/reactable-pagination.css';
import 'antd/dist/antd.css';



appSetup();  // 加载ajax


initJQueryAjax(); // 设置token

const analysisShowContainer = document.getElementById('js-add-slice-container');
const bootstrapData = JSON.parse(analysisShowContainer.getAttribute('data-bootstrap'));

ReactDOM.render(
    <div>
      <ShowResult
          log_dir_id={bootstrapData.log_dir_id}
          description_img={bootstrapData.description_img}
          model_result_execl_bs={bootstrapData.model_result_execl_bs}
      />
    </div>,
  analysisShowContainer,
);