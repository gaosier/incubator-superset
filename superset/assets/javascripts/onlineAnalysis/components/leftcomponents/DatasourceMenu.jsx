import React, {Component} from 'react';
import {Select, Button, Icon} from 'antd';
import {
    get_all_model,
    getcode,
    set_model,
    get_all_filter_column,
    get_all_version,
    choice_version
} from '../../actions/leftmenu';
import {connect} from "react-redux";
import {
    Modal
} from 'react-bootstrap';

import Datasource from './Datasource';
import axios from "axios";


class DatasourceMenu extends Component {
    constructor(props) {
        super(props);
        this.state = {
            load_all_modal: true,
            load_all_version: true,
            show_code_modal: false,
            code: null,
            loading_code: true
        };
    }

    componentDidMount() {
        this.props.get_all_filter_column(this.props.leftmenu.datasource_id);
    }

    show_all_modal_name() {
        if (this.state.load_all_modal) {
            const {get_all_model} = this.props;
            get_all_model();
            this.setState({
                load_all_modal: false
            })
        }
    }

    show_all_version_name() {
        console.log(this.props.leftmenu);
        this.props.get_all_version(this.props.leftmenu.form_data.name);
    }

    change_version(value) {
        this.props.choice_version(value, this.props.leftmenu.slice.all_version);
        console.log(value);
    }

    render_version() {
        console.log(this.props.leftmenu.slice.all_version['v1.0']);
        return Object.keys(this.props.leftmenu.slice.all_version).map((element, index) =>
            <Select.Option key={index} value={element}> {element}</Select.Option>);
    }

    change_model(value) {
        if (value === undefined) {
            value = '';
        }
        const {set_model} = this.props;
        set_model(value);
    }

    render_modal_options() {
        return this.props.leftmenu.slice.all_model.map((element, index) =>
            <Select.Option key={index} value={element}> {element}</Select.Option>);
    }

    toggleCode() {
        this.setState({show_code_modal: !this.state.show_code_modal});
    }

    onEnterCode() {
        if (this.state.code === null) {
            axios.get('/online/preview/code/')
                .then(res => {
                    this.setState({
                        code: res.data.code,
                        loading_code: false
                    })
                })
                .catch(error => {

                })
        }
    }

    render_code_model() {
        return (
            <Modal
                show={this.state.show_code_modal}
                onHide={this.toggleCode.bind(this)}
                onEnter={this.onEnterCode.bind(this)}
                bsSize="large"
                dialogClassName="custom-modal"
            >
                <Modal.Header closeButton>
                    <Modal.Title>查看代码</Modal.Title>
                </Modal.Header>
                <Modal.Body>
                    {this.state.loading_code &&
                    <img
                        className="loading"
                        alt="Loading..."
                        src="../../../../../static/assets/images/loading.gif"
                    />
                    }
                    <div dangerouslySetInnerHTML={{__html: this.state.code}}/>
                </Modal.Body>
                <Modal.Footer>
                    <Button onClick={this.toggleCode.bind(this)}>Close</Button>
                </Modal.Footer>
            </Modal>
        )
    }

    render_sk_type() {
        if (this.props.leftmenu.form_data.sk_type === '') {
            return (
                <div>
                    <Select
                        value={undefined}
                        placeholder="请选择模型名称"
                        showSearch
                        style={{width: 200}}
                        searchPlaceholder="输入"
                        onFocus={this.show_all_modal_name.bind(this)}
                        onChange={this.change_model.bind(this)}
                    >
                        {this.render_modal_options()}
                    </Select>
                </div>
            )
        } else {
            return (
                <div>
                    <Select
                        value={this.props.leftmenu.form_data.sk_type}
                        showSearch
                        style={{width: 200}}
                        searchPlaceholder="输入"
                        onFocus={this.show_all_modal_name.bind(this)}
                        onChange={this.change_model.bind(this)}
                    >
                        {this.render_modal_options()}
                    </Select>
                </div>
            )
        }
    }

    render_select_version() {
        if (this.props.leftmenu.form_data.version === '') {
            return (
                <div>
                    <Select
                        value={undefined}
                        disabled={true}
                        defaultValue="未找到对应的版本号"
                        showSearch style={{width: 200}}
                        onFocus={this.show_all_version_name.bind(this)}
                        searchPlaceholder="输入"
                    >
                        {this.render_version()}
                    </Select>
                </div>
            )

        } else {
            return (
                <div>
                    <Select
                        value={this.props.leftmenu.form_data.version}
                        showSearch
                        style={{width: 200}}
                        searchPlaceholder="输入"
                        onFocus={this.show_all_version_name.bind(this)}
                        onChange={this.change_version.bind(this)}
                    >
                        {this.render_version()}
                    </Select>
                </div>
            )
        }
    }

    render() {
        return (
            <div>
                <div id="datasource">
                    <span>数据源</span>
                </div>
                <div>
                    <Datasource>
                    </Datasource>
                </div>
                <div id="model-show">
                    <span>模型名称</span>
                    {this.render_sk_type()}
                    <Button onClick={this.toggleCode.bind(this)}><Icon type="search"/>预览代码</Button>
                    {this.render_code_model()}
                </div>
                <div>
                    <span>版本名称</span>
                    {this.render_select_version()}
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
    get_all_model,
    set_model,
    get_all_filter_column,
    get_all_version,
    choice_version
})(DatasourceMenu);
