import React, {Component} from 'react';
import {Select, Input, Checkbox} from 'antd';
import {connect} from "react-redux";
import {
    get_datasource_columns,
    delete_variable_box,
    modify_variable_box_field,
    modify_variable_box_bins,
    modify_variable_box_labels,
    modify_include_endpoint
} from '../../actions/leftmenu';

class Variablebox extends Component {
    constructor(props) {
        super(props);
    }

    render_select() {
        return (this.props.leftmenu.slice.all_select_column.map((res, index) => {
            return (<Select.Option key={index} value={res.name}>{res.verbose_name}</Select.Option>)
        }))

    }

    delete_variable() {
        this.props.delete_variable_box(this.props.variable_key);
    }

    change_select(value) {
        this.props.modify_variable_box_field(this.props.variable_key, value);
    }

    render_select_columns() {
        if (this.props.field === "") {
            return (
                <div className="space-1 row">
                    <div className="col-md-12">
                        <Select
                            value={undefined}
                            placeholder="请选择要进行变量分箱的列"
                            showSearch
                            style={{width: 400}}
                            searchPlaceholder="输入"
                            onChange={this.change_select.bind(this)}
                        >
                            {this.render_select()}
                        </Select>
                    </div>
                </div>
            )
        } else {
            return (
                <div className="space-1 row">
                    <div className="col-md-12">
                        <Select
                            value={this.props.field}
                            showSearch
                            placeholder="请选择要进行变量分箱的列"
                            style={{width: 400}}
                            searchPlaceholder="输入"
                            onChange={this.change_select.bind(this)}
                        >
                            {this.render_select()}
                        </Select>
                    </div>
                </div>
            )
        }
    }

    change_bins(e) {
        this.props.modify_variable_box_bins(this.props.variable_key, e.target.value);
    }

    change_labels(e) {
        this.props.modify_variable_box_labels(this.props.variable_key, e.target.value);
    }

    render_input_bins() {
        if (this.props.bins === '') {
            return (
                <div className="col-md-5">
                    <Input
                        value={undefined}
                        placeholder="范围:0,100,200,300"
                        onChange={this.change_bins.bind(this)}
                    />
                </div>
            )
        } else {
            return (
                <div className="col-md-5">
                    <Input
                        placeholder="范围:0,100,200,300"
                        value={this.props.bins}
                        onChange={this.change_bins.bind(this)}
                    />
                </div>
            )
        }
    }

    render_checkbox() {
        return (
            <div className="col-md-7">
                <Checkbox checked={this.props.left} onChange={this.change_checkbox.bind(this)}
                          value="left">是否包含左端点</Checkbox>
                <Checkbox checked={this.props.right} onChange={this.change_checkbox.bind(this)}
                          value="right">是否包含右端点</Checkbox>
            </div>
        )
    }

    change_checkbox(e) {
        this.props.modify_include_endpoint(this.props.variable_key, e.target.checked, e.target.value);
    }

    render_input_lables() {
        if (this.props.labels === '') {
            return (
                <div className="col-md-8">
                    <Input
                        value={undefined}
                        placeholder="替换值:0,1,2,3"
                        onChange={this.change_labels.bind(this)}
                    />
                </div>
            )
        } else {
            return (
                <div className="col-md-8">
                    <Input
                        value={this.props.labels}
                        placeholder="替换值:0,1,2,3"
                        onChange={this.change_labels.bind(this)}
                    />
                </div>
            )
        }
    }

    render() {
        return (
            <div>
                {this.render_select_columns()}
                <div className="space-1 row">
                    {this.render_input_bins()}
                    {this.render_checkbox()}
                </div>
                <div className="space-1 row">
                    {this.render_input_lables()}
                    <div className="col-md-4">
                        <button
                            id="remove-button"
                            type="button"
                            className="btn btn-sm btn-default"
                            onClick={this.delete_variable.bind(this)}
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
    delete_variable_box,
    modify_variable_box_field,
    modify_variable_box_bins,
    modify_variable_box_labels,
    modify_include_endpoint
})(Variablebox);
