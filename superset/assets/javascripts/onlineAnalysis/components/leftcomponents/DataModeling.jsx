import React, {Component} from 'react';
import {connect} from 'react-redux';
import {Button, Divider, Card, Input, Select} from 'antd';
import {Tabs, Tab, Modal, Table} from 'react-bootstrap';
import TrainDataset from '../leftcomponents/TrainDataset';
import ValidataDataset from '../leftcomponents/ValidataDataset';
import {add_train_dataset, add_validate_datasets, get_model_parameter, modify_parameter} from '../../actions/leftmenu';

class DataModeling extends Component {

    constructor(props) {
        super(props);
        this.state = {
            show_Modal: false
        };
        this.toggleModal = this.toggleModal.bind(this);
        this.onEnterModel = this.onEnterModel.bind(this);
        this.closeModal = this.closeModal.bind(this);
    }

    close_model() {
        this.setState({
            show_Modal: !this.state.show_Modal
        })
    }

    toggleModal() {

        const sk_type = this.props.leftmenu.form_data.sk_type;
        const now_modal = this.props.leftmenu.form_data.model_param;
        if (Object.keys(now_modal).length === 0) {
            this.props.get_model_parameter(sk_type);
        }
        this.setState({show_Modal: !this.state.show_Modal});
    }

    closeModal() {
        this.setState({show_Modal: !this.state.show_Modal});
    }

    onEnterModel() {


    }

    change_x_col(dum, cop, value) {
        this.props.modify_parameter(dum, cop, value);
    }

    render_column() {
        return (this.props.leftmenu.slice.all_select_column.map((res, index) => {
            return (<Select.Option key={index} value={res.name}>{res.verbose_name}</Select.Option>)
        }))

    }

    show_param() {
        const keys = Object.keys(this.props.leftmenu.form_data.model_param);
        return (keys.map((dum, index) => {
            return (<Card
                title={dum}
                style={{width: 800}}
                key={index}
            >
                <div>
                    {this.render_pa(dum)}
                </div>
            </Card>)
        }))
    }

    render_pa(dum) {
        const name = this.props.leftmenu.form_data.model_param[dum];
        return (Object.keys(name).map((cop, index) => (
            <div key={index}>
                <span>{cop}</span>
                {this.render_input(dum, cop)}
                <span>{}</span>
            </div>
        )))
    }

    render_input(dum, cop) {
        if (Array.isArray(this.props.leftmenu.form_data.model_param[dum][cop])) {
            return (
                <div>
                    <Select
                        style={{width: 606}}
                        value={this.props.leftmenu.form_data.model_param[dum][cop]}
                        showSearch
                        mode="multiple"
                        placeholder="请选择列"
                        searchPlaceholder="输入"
                        onChange={this.change_x_col.bind(this, dum, cop)}

                    >
                        {this.render_column()}
                    </Select>
                </div>
            )
        } else {
            if (this.props.leftmenu.form_data.model_param === '' && this.props.leftmenu.form_data.model_param === []) {
                return (<Input
                    value={undefined}
                    placeholder="请输入变量值"
                    onChange={this.change_input_name.bind(this, dum, cop)}
                />)
            } else {
                return (<Input
                    value={this.props.leftmenu.form_data.model_param[dum][cop]}
                    placeholder="请输入变量值"
                    onChange={this.change_input_name.bind(this, dum, cop)}
                />)
            }
        }
    }

    change_input_name(dum, cop, e) {
        this.props.modify_parameter(dum, cop, e.target.value);
    }

    render_model_param() {
        return (
            <Modal
                show={this.state.show_Modal}
                onHide={this.closeModal}
                onEnter={this.onEnterModal}
                bsSize="lg">
                <Modal.Header closeButton>
                    <Modal.Title>模型参数</Modal.Title>
                </Modal.Header>
                <Modal.Body>
                    <div>
                        {this.show_param()}
                    </div>
                </Modal.Body>
                <Modal.Footer>
                    <Button onClick={this.close_model.bind(this)}>关闭</Button>
                </Modal.Footer>

            </Modal>)

    }


    render_train() {
        return (this.props.leftmenu.form_data.train_dataset.map((dum, index) => (
            <TrainDataset
                col={dum.col}
                op={dum.op}
                val={dum.val}
                key={index}
                train_key={index}
            />
        )))
    }


    render_validata() {
        return (
            this.props.leftmenu.form_data.validate_datasets.map((dum, index) => (
                <ValidataDataset
                    name={dum.name}
                    filters={dum.filters}
                    val_key={index}
                    key={index}
                />
            ))

        )
    }

    add_train() {
        this.props.add_train_dataset();
    }

    add_vali() {
        this.props.add_validate_datasets();
    }

    render() {
        return (
            <div>
                <div>
                    <Divider>跑模型数据集</Divider>
                    {this.render_train()}
                    <Button onClick={this.add_train.bind(this)}>添加跑模型数据集</Button>

                </div>
                <div>
                    <Divider>验证数据集</Divider>
                    {this.render_validata()}
                    <Button onClick={this.add_vali.bind(this)}>添加验证数据集</Button>
                </div>
                <div>
                    <Divider>模型参数</Divider>
                    {this.render_model_param()}
                    <Button onClick={this.toggleModal.bind(this)}>模型参数</Button>
                </div>
            </div>
        );
    }
}

const mapStateToProps = (state) => {
    return {
        leftmenu: state.leftmenu,
    }
};

export default connect(mapStateToProps, {
    add_train_dataset,
    add_validate_datasets,
    get_model_parameter,
    modify_parameter
})(DataModeling);
