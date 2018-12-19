import React, {Component} from 'react';
import {Collapse, Button, Icon, Input, Radio, notification} from 'antd';
import {connect} from 'react-redux';
import 'antd/dist/antd.css';
import DatasourceMenu from './leftcomponents/DatasourceMenu';
import DescriptiveAnalysis from "./leftcomponents/DescriptiveAnalysis";
import DataPreprocessing from "./leftcomponents/DataPreprocessing";
import DataModeling from "./leftcomponents/DataModeling";
import {run_model, set_name, set_version, set_run, save_all_model} from '../actions/leftmenu';
import {Modal} from 'react-bootstrap';

const Panel = Collapse.Panel;
const RadioGroup = Radio.Group;

class LeftMenu extends Component {

    constructor(props) {
        super(props);
        this.state = {
            show_save_modal: false,
            chose_action: '',
            name: this.props.leftmenu.form_data.name,
            version: this.props.leftmenu.form_data.version,
            saves_name: '',
            can_add: !this.props.leftmenu.can_add || false,
            can_overwrite: !this.props.leftmenu.can_overwrite || false,
        };
        this.toggle_modal = this.toggle_modal.bind(this);
        this.save_allmodal = this.save_allmodal.bind(this);
    }

    run_modul() {
        this.props.set_run();
        this.props.run_model(this.props.leftmenu.form_data);
    }


    save_model() {
        this.setState({
            show_save_modal: !this.state.show_save_modal
        })
    }

    toggle_modal() {
        this.setState({
            show_save_modal: !this.state.show_save_modal
        })
    }

    close_modal() {
        this.setState({
            show_save_modal: !this.state.show_save_modal
        })
    }

    render_save_info() {
        if (this.state.name === '') {
            const radioStyle = {
                display: 'block',
                height: '30px',
                lineHeight: '30px',
            };
            return (
                <div>
                    <div>
                        <RadioGroup onChange={this.change_action.bind(this)} value={this.state.chose_action}>
                            <Radio style={radioStyle} value="saveas" disabled={this.state.can_add}>另存为
                                {this.state.chose_action === 'saveas' ? <Input
                                    value={this.state.saves_name}
                                    style={{width: 150}}
                                    placeholder="请输入分析模型名称"
                                    onChange={this.change_saves_name.bind(this)}
                                /> : null}</Radio>
                        </RadioGroup>
                    </div>
                    {this.render_version()}
                </div>
            )
        } else {
            console.log('state', this.state.can_overwrite, this.state.can_add);
            const radioStyle = {
                display: 'block',
                height: '30px',
                lineHeight: '30px',
            };
            return (
                <div>
                    <div>
                        <RadioGroup onChange={this.change_action.bind(this)} value={this.state.chose_action}>
                            <Radio style={radioStyle} value="overwrite"
                                   disabled={this.state.can_overwrite}>更新 {this.state.name}</Radio>
                            <Radio style={radioStyle} value="saveas" disabled={this.state.can_add}>另存为
                                {this.state.chose_action === 'saveas' ? <Input
                                    style={{width: 150}}
                                    value={this.state.saves_name}
                                    placeholder="请输入分析模型名称"
                                    onChange={this.change_saves_name.bind(this)}
                                /> : null}</Radio>
                        </RadioGroup>
                    </div>
                    {this.render_version()}
                </div>
            )
        }
    }

    change_action(e) {
        console.log(e.target.value);
        this.setState({
            chose_action: e.target.value
        })
    }

    model_save() {
        this.props.set_name(this.state.name);
        this.props.set_version(this.state.version);
        this.setState({
            show_save_model: !this.state.show_save_model
        });
        console.log(111, this.props.leftmenu.form_data.analysis_id);
        if (this.state.chose_action === 'saveas') {
            this.save_allmodal(this.props.leftmenu.form_data, this.props.leftmenu.datasource_id, this.state.chose_action, this.state.saves_name, this.state.version);
            // this.props.save_allmodal(this.props.leftmenu.form_data,this.props.leftmenu.datasource_id,this.state.chose_action,this.state.saves_name,this.state.version);
        } else if (this.state.chose_action === 'overwrite') {
            this.save_allmodal(this.props.leftmenu.form_data, this.props.leftmenu.datasource_id, this.state.chose_action, this.state.name, this.state.version);
            // this.props.save_allmodal(this.props.leftmenu.form_data,this.props.leftmenu.datasource_id,this.state.chose_action,this.state.name,this.state.version);
        }

    }

    render_version() {
        if (this.state.version === '') {
            return (
                <div id="version">
                    <span>版本名称</span>
                    &nbsp; &nbsp;
                    <Input
                        value={undefined}
                        style={{width: 150}}
                        placeholder="请输入分析模型名称"
                        onChange={this.change_version.bind(this)}
                    />
                </div>
            )
        } else {
            return (
                <div id="version">
                    <span>版本名称</span>
                    &nbsp; &nbsp;
                    <Input
                        value={this.state.version}
                        style={{width: 150}}
                        placeholder="请输入分析模型名称"
                        onChange={this.change_version.bind(this)}
                    />
                </div>
            )
        }
    }

    save_allmodal(form_data, id, action, name, version) {
        delete form_data.version;
        delete form_data.analysis_name;
        $.ajax({
            type: 'POST',
            url: "/online/analysis/table/" + id + '/?action=' + action + '&name=' + name + '&version=' + version,
            data: {
                form_data: JSON.stringify(form_data),
            },
            success: ((data) => {
                console.log(data);
                const analysis_id = data.slice.id;
                console.log(analysis_id);
                const url = window.location.href.split('?')[0];
                console.log(url);
                const new_url = encodeURI(url + '?form_data={"analysis_id":' + analysis_id + '}');
                console.log(new_url);
                window.open(new_url, '_self');
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

    change_version(e) {
        this.setState({
            version: e.target.value
        })
    }

    change_name(e) {
        this.setState({
            saves_name: e.target.value
        })
    }

    change_saves_name(e) {
        this.setState({
            saves_name: e.target.value
        })
    }

    render_save_modal() {
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
                    <Button onClick={this.save_model.bind(this)}><Icon type="plus-circle" theme="filled"/>保存</Button>
                </div>
                {this.render_save_modal()}
                <div className="make">
                    <Collapse defaultActiveKey={['1', '2', '3', '4']}>
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

export default connect(mapStateToProps, {run_model, set_name, set_version, set_run})(LeftMenu);