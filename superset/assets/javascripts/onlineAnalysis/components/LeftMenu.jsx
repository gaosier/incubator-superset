import React, { Component } from 'react';
import { Collapse, Button, Icon } from 'antd';
import { connect } from 'react-redux';
import 'antd/dist/antd.css';
import DatasourceMenu from './leftcomponents/DatasourceMenu';
import DescriptiveAnalysis from "./leftcomponents/DescriptiveAnalysis";
import DataPreprocessing from "./leftcomponents/DataPreprocessing";
import DataModeling from "./leftcomponents/DataModeling";
import { run_model } from '../actions/leftmenu';

const Panel = Collapse.Panel;
class LeftMenu extends Component {

    run_modul(){
        console.log('run');
        this.props.run_model(this.props.leftmenu.form_data);
    }

    render() {
        return (
            <div>
                <div className="TopBtn">
                    <Button onClick={this.run_modul.bind(this)}><Icon type="play-circle" theme="filled"/>运行</Button>
                    <Button><Icon type="plus-circle" theme="filled" />保存</Button>
                </div>
                <div className="make">
                    <Collapse defaultActiveKey={['1','2','3','4']} >
                        <Panel header="数据源/模型选择" key="1">
                        <DatasourceMenu/>
                        </Panel>
                        <Panel header="数据预处理" key="2">
                        <DescriptiveAnalysis/>
                        </Panel>
                        <Panel header="描述分析" key="3">
                        <DataPreprocessing/>
                        </Panel>
                        <Panel header="数据建模" key="4">
                        <DataModeling/>
                        </Panel>
                    </Collapse>
                </div>
            </div>
        )
    }
}

const mapStateToProps = (state) => {
    return {
        leftmenu: state.leftmenu,
    }
};

export default connect(mapStateToProps,{run_model})(LeftMenu);