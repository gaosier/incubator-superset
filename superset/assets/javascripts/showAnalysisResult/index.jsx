import React from 'react';
import ReactDOM from 'react-dom';
import {appSetup} from "../common";
import {initJQueryAjax} from "../modules/utils";
import ShowResult  from './ShowResult';
import '../../stylesheets/reactable-pagination.css';
import 'antd/dist/antd.css';



appSetup();  // 加载ajax


initJQueryAjax(); // 设置token

const analysisViewContainer = document.getElementById('app');

ReactDOM.render(
    <div>
      <ShowResult />
    </div>,
  analysisViewContainer,
);