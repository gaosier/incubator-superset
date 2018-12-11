import React, {Component} from 'react';
import {Select, Input} from 'antd';
import {connect} from 'react-redux';
import {get_datasource_columns, modify_dummy_field, modify_dummy_value, delete_dummy} from '../../actions/leftmenu';
import axios from "axios/index";

class Dummy extends Component {
    constructor(props) {

        super(props);
        console.log(props);
        this.state = {
            all_choice_column: []
        }

    }

    // componentDidMount() {
    //     this.props.get_datasource_columns(this.props.leftmenu.datasource_id);
    // }

    delete_dummy_comp() {
        this.props.delete_dummy(this.props.dummy_key);
    }

    change_select(value) {
        this.props.modify_dummy_field(this.props.dummy_key, value);
    }

    change_labels(e) {
        this.props.modify_dummy_value(this.props.dummy_key, e.target.value);
    }

    show_all_name() {
        axios.get("/online/columns/table/" + this.props.leftmenu.datasource_id + "/")
            .then(res => {
                    this.setState({
                        all_choice_column: res.data
                    })
                }
            )
            .catch(error => {
                console.log(error);
            })
    }

    render_input() {
        if (this.props.labels === '') {
            return (
                <Input
                    value={undefined}
                    placeholder="格式为{男:1,女:2}"
                    onChange={this.change_labels.bind(this)}
                />
            )
        } else {
            console.log(this.props.labels);
            return (
                <Input
                    value={this.props.labels}
                    // value={this.props.labels}
                    placeholder="格式为{男:1,女:2}"
                    onChange={this.change_labels.bind(this)}
                />
            )
        }
    }

    render_select() {
        console.log(11189898998);
        let a = 0;
        return (this.state.all_choice_column.map(res => {
            return (<Select.Option key={a++} value={res.name}>{res.verbose_name}</Select.Option>)
        }))
    }

    render_select_columns() {
        console.log('重新刷新');
        if (this.props.field === '') {
            return (
                <Select
                    value={undefined}
                    placeholder="请选择要进行变量分箱的列"
                    style={{width: 200}}
                    searchPlaceholder="输入"
                    onFocus={this.show_all_name.bind(this)}
                    onChange={this.change_select.bind(this)}>
                    {this.render_select()}
                </Select>
            )
        } else {
            return (
                <Select
                    value={this.props.field}
                    placeholder="请选择要进行变量分箱的列"
                    style={{width: 150}}
                    searchPlaceholder="输入"
                    onFocus={this.show_all_name.bind(this)}
                    onChange={this.change_select.bind(this)}>
                    {this.render_select()}
                </Select>
            )
        }
    }

    render() {
        return (
            <div>
                <div className="space-1 row">
                    <div className="col-md-6">
                        {this.render_select_columns()}
                    </div>
                    <div className="col-md-4">
                        {this.render_input()}
                    </div>
                    <div className="col-md-2">
                        <button
                            id="remove-button"
                            type="button"
                            className="btn btn-sm btn-default"
                            onClick={this.delete_dummy_comp.bind(this)}
                        >
                            <i className="fa fa-minus"></i></button>
                    </div>
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
    get_datasource_columns,
    modify_dummy_field,
    modify_dummy_value,
    delete_dummy
})(Dummy);
