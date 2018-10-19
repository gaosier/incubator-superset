import React from 'react';
import ReactDOM from 'react-dom';
import App from './App';
import { appSetup } from '../common';
import { initJQueryAjax } from '../modules/utils';


appSetup();
initJQueryAjax();

const exploreViewContainer = document.getElementById('app');

ReactDOM.render(
    <App />,
  exploreViewContainer
);