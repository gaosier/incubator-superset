import React, {Component} from 'react';
import {Select} from 'antd';
import {connect} from 'react-redux';
import {
    get_datasource_columns,
    delete_correlation,
    modify_correlation_field,
    modify_correlation_two,
    modify_correlation_last
} from '../../actions/leftmenu';
import axios from "axios/index";

class CorrelationAnalysis extends Component {
    constructor(props) {
        super(props);
        this.state={
            all_choice_column:[]
        }
    }

    // componentDidMount() {
    //     this.props.get_datasource_columns(this.props.leftmenu.datasource_id);
    // }

    show_all_name(){
        axios.get("/online/columns/table/"+this.props.leftmenu.datasource_id+"/")
            .then(res=>{
                this.setState({
                    all_choice_column:res.data
                })
                }
            )
    }

    delete_corre() {
        this.props.delete_correlation(this.props.correlation_key);
    }

    change_select(value) {
        this.props.modify_correlation_field(this.props.correlation_key, value);
    }

    change_select_type(value) {
        this.props.modify_correlation_last(this.props.correlation_key, value);
    }

    change_select_props(value) {
        this.props.modify_correlation_two(this.props.correlation_key, value);
    }

    render_select() {
        console.log(11189898998);
        let a = 0;
        return (this.state.all_choice_column.map(res => {
            return (<Select.Option key={a++} value={res.name}>{res.verbose_name}</Select.Option>)
        }))
    }

    render_draw_props() {
        if (this.props.handle_props === 0) {
            return (
                <Select
                    value={undefined}
                    style={{width: 106}}
                    placeholder="请选择方法"
                    searchPlaceholder="输入"
                    onChange={this.change_select_props.bind(this)}
                >
                    <Select.Option key={1} value="pie">pie</Select.Option>
                    <Select.Option key={2} value="countplot">countplot</Select.Option>

                </Select>
            )
        } else {
            return (
                <Select
                    style={{width: 106}}
                    value={this.props.handle_props}
                    placeholder="请选择方法"
                    searchPlaceholder="输入"
                    onChange={this.change_select_props.bind(this)}
                >
                    <Select.Option key={1} value="pie">pie</Select.Option>
                    <Select.Option key={2} value="countplot">countplot</Select.Option>

                </Select>
            )
        }
    }

    render_draw_type() {
        if (this.props.handle_type === 0) {
            return (
                <Select
                    value={undefined}
                    style={{width: 270}}
                    placeholder="请选择类型"
                    searchPlaceholder="输入"
                    onChange={this.change_select_type.bind(this)}
                >
                    <Select.Option key={1} value="matloplib">matloplib</Select.Option>
                    <Select.Option key={2} value="seaborn">seaborn</Select.Option>

                </Select>
            )
        } else {
            return (
                <Select
                    style={{width: 270}}
                    value={this.props.handle_type}
                    placeholder="请选择类型"
                    searchPlaceholder="输入"
                    onChange={this.change_select_type.bind(this)}
                >
                    <Select.Option key={1} value="matloplib">matloplib</Select.Option>
                    <Select.Option key={2} value="seaborn">seaborn</Select.Option>

                </Select>
            )
        }
    }

    render_select_columns() {
        if (this.props.field === 0) {
            return (
                <Select
                    value={undefined}
                    style={{width: 484}}
                    placeholder="请选择列名"
                    searchPlaceholder="输入"
                    onFocus={this.show_all_name.bind(this)}
                    onChange={this.change_select.bind(this)}
                >
                    {this.render_select()}
                </Select>
            )
        } else {
            return (
                <Select
                    style={{width: 484}}
                    value={this.props.field}
                    placeholder="请选择列名"
                    searchPlaceholder="输入"
                    onFocus={this.show_all_name.bind(this)}
                    onChange={this.change_select.bind(this)}
                >
                    {this.render_select()}
                </Select>
            )
        }
    }

    render() {
        return (
            <div>
                <div className="space-1 row">
                    <div className="col-md-12">
                        {this.render_select_columns()}
                    </div>
                </div>
                <div className="space-1 row">
                    <div className="col-md-3">
                        {this.render_draw_props()}
                    </div>
                    <div className="col-md-7">
                        {this.render_draw_type()}
                    </div>
                    <div className="col-md-2">
                        <button
                            id="remove-button"
                            type="button"
                            className="btn btn-sm btn-default"
                            onClick={this.delete_corre.bind(this)}
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

export default connect(mapStateToProps,
    {
        get_datasource_columns,
        delete_correlation,
        modify_correlation_field,
        modify_correlation_two,
        modify_correlation_last
    })(CorrelationAnalysis);
