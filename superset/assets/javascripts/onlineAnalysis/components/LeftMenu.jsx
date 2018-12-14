import React, { Component } from 'react';
import { Collapse, Button, Icon, Input } from 'antd';
import { connect } from 'react-redux';
import 'antd/dist/antd.css';
import DatasourceMenu from './leftcomponents/DatasourceMenu';
import DescriptiveAnalysis from "./leftcomponents/DescriptiveAnalysis";
import DataPreprocessing from "./leftcomponents/DataPreprocessing";
import DataModeling from "./leftcomponents/DataModeling";
import { run_model,set_name, set_version,save_allmodal } from '../actions/leftmenu';
import { Modal } from 'react-bootstrap';

const Panel = Collapse.Panel;
class LeftMenu extends Component {

    constructor(props){
        super(props);
        this.state={
            show_save_modal:false,
            name:this.props.leftmenu.form_data.analysis_name,
            version:this.props.leftmenu.form_data.version
        };
        this.toggle_modal = this.toggle_modal.bind(this);
    }

    run_modul(){
        this.props.run_model(this.props.leftmenu.form_data);
    }


    save_model(){
        this.setState({
            show_save_modal:!this.state.show_save_modal
        })
    }

    toggle_modal(){
        this.setState({
            show_save_modal:!this.state.show_save_modal
        })
    }

    close_modal(){
        this.setState({
            show_save_modal:!this.state.show_save_modal
        })
    }

    render_save_info(){
        if(this.state.name=== ''){
            return(
                <div>
                <div>
                    <span>分析模型名称</span>
                    <Input
                        value={undefined}
                        placeholder="请输入分析模型名称"
                        onChange={this.change_name.bind(this)}
                    />

                </div>
                     {this.render_version()}
                </div>
            )
        }else{
            return(
                <div>
                <div>
                    <span>分析模型名称</span>
                    <Input
                        value={this.state.name}
                        placeholder="请输入分析模型名称"
                        onChange={this.change_name.bind(this)}
                    />

                </div>
                    {this.render_version()}
                </div>
            )
        }
    }
    model_save(){
        this.props.set_name(this.state.name);
        this.props.set_version(this.state.version);
        this.setState({
            show_save_model:!this.state.show_save_model
        });
        console.log(111,this.props.leftmenu.form_data.analysis_id);
        if(this.props.leftmenu.form_data.analysis_id === ''){
            console.log('saves');
            var action = "saveas";
        }else{
            var action = "overwrite";
            console.log('overwrite');
        }
        this.props.save_allmodal(this.props.leftmenu.form_data,this.props.leftmenu.datasource_id,action,this.state.name,this.state.version);
    }
    render_version(){
        if(this.state.version === ''){
            return(
                <div>
                    <span>版本名称</span>
                    <Input
                        value={undefined}
                        placeholder="请输入分析模型名称"
                        onChange={this.change_version.bind(this)}
                        />
                </div>
            )
        }else{
            return(
                <div>
                    <span>版本名称</span>
                    <Input
                        value={this.state.version}
                        placeholder="请输入分析模型名称"
                        onChange={this.change_version.bind(this)}
                        />
                </div>
            )
        }
    }
    change_version(e){
        this.setState({
            version:e.target.value
        })
    }

    change_name(e){
        this.setState({
            name:e.target.value
        })
    }
    render_save_modal(){
        return (
            <Modal
                show={this.state.show_save_modal}
                onHide={this.toggle_modal}
                bsSize="lg"
            >

                <Modal.Header closeButton>
                    <Modal.Title>保存模型</Modal.Title>
                </Modal.Header>
                <Modal.Body>
                    {this.render_save_info()}
                </Modal.Body>
                <Modal.Footer>
                    <Button onClick={this.close_modal.bind(this)}>关闭</Button>
                    <Button onClick={this.model_save.bind(this)}>保存</Button>
                </Modal.Footer>
            </Modal>
        )
    }

    render() {
        return (
            <div>
                <div className="TopBtn">
                    <Button onClick={this.run_modul.bind(this)}><Icon type="play-circle" theme="filled"/>运行</Button>
                    <Button onClick={this.save_model.bind(this)}><Icon type="plus-circle" theme="filled" />保存</Button>
                </div>
                {this.render_save_modal()}
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

export default connect(mapStateToProps,{run_model, set_name, set_version,save_allmodal})(LeftMenu);