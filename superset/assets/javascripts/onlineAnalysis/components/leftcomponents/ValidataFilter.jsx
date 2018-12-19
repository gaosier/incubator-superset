import React, {Component} from 'react';
import {connect} from 'react-redux';
import {Button, Select, Input} from 'antd';
import {
    get_datasource_columns,
    modify_filter_col,
    modify_filter_op,
    modify_filter_val,
    delete_vali_filters
} from '../../actions/leftmenu';
import axios from "axios/index";

class ValidataFilter extends Component {
    constructor(props) {
        super(props);
        this.state = {
            value_column: []
        }
    }

    change_select_col(value) {
        this.props.modify_filter_col(this.props.val_key, this.props.filter_key, value);
        axios.get("/online/filter/table/" + this.props.leftmenu.datasource_id + '/' + value + '/')
            .then(res => {
                this.setState({
                    value_column: res.data
                })
            })
            .catch(error => {
                notification['error']({
                    message: '获取参数失败',
                    description: '获取参数失败,详情请咨询相关人员.',
                });
            })
    }

    change_select_op(value) {
        this.props.modify_filter_op(this.props.val_key, this.props.filter_key, value);
    }

    change_select_value(value) {
        this.props.modify_filter_val(this.props.val_key, this.props.filter_key, value);
    }

    delete_comp() {
        this.props.delete_vali_filters(this.props.val_key, this.props.filter_key);
    }

    render_select_columns() {
        return (this.props.leftmenu.slice.all_select_column.map((res, index) => {
            return (<Select.Option key={index} value={res.name}>{res.verbose_name}</Select.Option>)
        }))
    }

    render_select_col() {
        if (this.props.col === "") {
            return (
                <Select
                    value={undefined}
                    style={{width: 484}}
                    placeholder="请选择列名"
                    searchPlaceholder="输入"
                    onChange={this.change_select_col.bind(this)}
                >
                    {this.render_select_columns()}
                </Select>
            )
        } else {
            return (
                <Select
                    value={this.props.col}
                    style={{width: 484}}
                    placeholder="请选择列名"
                    searchPlaceholder="输入"
                    onChange={this.change_select_col.bind(this)}>
                    {this.render_select_columns()}
                </Select>
            )
        }
    }

    render_select_op() {
        if (this.props.op === "") {
            return (
                <Select
                    value={undefined}
                    style={{width: 106}}
                    showSearch
                    placeholder="选择运算符"
                    searchPlaceholder="输入"
                    onChange={this.change_select_op.bind(this)}>
                    <Select.Option key={1} value="==">==</Select.Option>
                    <Select.Option key={2} value=">=">>=</Select.Option>
                    <Select.Option key={3} value="<=">{"<="} </Select.Option>
                    <Select.Option key={4} value=">">{">"}</Select.Option>
                    <Select.Option key={5} value="<">{"<"}</Select.Option>

                </Select>
            )
        } else {
            return (
                <Select
                    value={this.props.op}
                    style={{width: 106}}
                    showSearch
                    placeholder="选择运算符"
                    searchPlaceholder="输入"
                    onChange={this.change_select_op.bind(this)}>
                    <Select.Option key={1} value="==">==</Select.Option>
                    <Select.Option key={2} value=">=">>=</Select.Option>
                    <Select.Option key={3} value="<=">{"<="} </Select.Option>
                    <Select.Option key={4} value=">">{">"}</Select.Option>
                    <Select.Option key={5} value="<">{"<"}</Select.Option>

                </Select>
            )
        }
    }

    render_select_value() {
        return (this.state.value_column.map((dum, index) => {
            return (<Select.Option key={index} value={dum}>{dum}</Select.Option>)
        }))
    }

    render_select_val() {
        if (this.props.val === "") {
            return (
                <Select
                    value={undefined}
                    style={{width: 246}}
                    showSearch
                    placeholder="输入过滤值"
                    searchPlaceholder="输入"
                    onChange={this.change_select_value.bind(this)}
                >
                    {this.render_select_value()}
                </Select>
            )
        } else {
            return (
                <Select
                    value={this.props.val}
                    showSearch
                    style={{width: 246}}
                    placeholder="输入过滤值"
                    searchPlaceholder="输入"
                    onChange={this.change_select_value.bind(this)}
                >
                    {this.render_select_value()}
                </Select>
            )
        }
    }


    render() {
        return (
            <div>
                <div className="space-1 row">
                    <div className="col-md-12">
                        {this.render_select_col()}
                    </div>
                </div>
                <div className="space-1 row">
                    <div className="col-md-3">
                        {this.render_select_op()}
                    </div>
                    <div className="col-md-7">
                        {this.render_select_val()}
                    </div>
                    <div className="col-md-2">
                        <button id="remove-button"
                                type="button"
                                className="btn btn-sm btn-default"
                                onClick={this.delete_comp.bind(this)}
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
    modify_filter_col,
    modify_filter_op,
    modify_filter_val,
    delete_vali_filters
})(ValidataFilter);
