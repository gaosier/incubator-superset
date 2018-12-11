import React, {Component} from 'react';
import { connect } from 'react-redux';
import { Button, Select, Input } from 'antd';
import { get_datasource_columns, modify_filter_col, modify_filter_op, modify_filter_val,delete_vali_filters } from '../../actions/leftmenu';

class ValidataFilter extends Component {
    constructor(props){
        super(props);
    }

    componentDidMount() {
        this.props.get_datasource_columns(this.props.leftmenu.datasource_id);
    }

    change_select_col(value){
        this.props.modify_filter_col(this.props.val_key,this.props.filter_key,value);
    }
    change_select_op(value){
        this.props.modify_filter_op(this.props.val_key,this.props.filter_key,value);
    }

    change_input_value(e){
        this.props.modify_filter_val(this.props.val_key,this.props.filter_key,e.target.value);
    }

    delete_comp(){
        this.props.delete_vali_filters(this.props.val_key,this.props.filter_key);
    }

    render_select_columns() {
        console.log(11189898998);
        let a = 0;
        return (this.props.leftmenu.slice.all_datasource_columns.metrics.map(res => {
            return (<Select.Option key={a++} value={res[0]}>{res[0]}</Select.Option>)
        }))
    }

    render_select_col(){
        if(this.props.col === ""){
            return(
                <Select
                    value={undefined}
                    style={{width: 484}}
                    placeholder="请选择列名"
                    searchPlaceholder="输入"
                    onChange={this.change_select_col.bind(this)}
                >
                    { this.render_select_columns() }
                </Select>
            )
        }else{
            return(
                <Select
                value={this.props.col}
                    style={{width: 484}}
                    placeholder="请选择列名"
                    searchPlaceholder="输入"
                    onChange={this.change_select_col.bind(this)}>
                    { this.render_select_columns() }
                </Select>
            )
        }
    }

    render_select_op(){
        if(this.props.op === ""){
            return(
                <Select
                value={undefined}
                    style={{width: 106}}
                    placeholder="选择运算符"
                    searchPlaceholder="输入"
                    onChange={this.change_select_op.bind(this)}>

                </Select>
            )
        }else{
            return(
                <Select
                value={this.props.op}
                    style={{width: 106}}
                    placeholder="选择运算符"
                    searchPlaceholder="输入"
                    onChange={this.change_select_op.bind(this)}>>

                </Select>
            )
        }
    }

    render_input_val(){
        if(this.props.val === ""){
            return(
                <Input
                    value={undefined}
                    placeholder="输入过滤值"
                    onChange={this.change_input_value.bind(this)}
                />
            )
        }else{
            return(
                <Input
                    value={this.props.val}
                    onChange={this.change_input_value.bind(this)}
                />
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
                        {this.render_input_val()}
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

export default connect(mapStateToProps,{ get_datasource_columns, modify_filter_col, modify_filter_op, modify_filter_val,delete_vali_filters })(ValidataFilter);
