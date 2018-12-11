import React, {Component} from 'react';
import { connect } from 'react-redux';
import { Button, Select, Input } from 'antd';
import { get_datasource_columns, delete_train_dataset, modify_train_col, modify_train_op, modify_train_val } from '../../actions/leftmenu';
import axios from "axios/index";

class TrainDataset extends Component {
    constructor(props){
        super(props);
        this.state={
            all_choice_column:[]
        }
    }

   show_all_name(){
        axios.get("/online/columns/table/"+this.props.leftmenu.datasource_id+"/")
            .then(res=>{
                this.setState({
                    all_choice_column:res.data
                })
                }
            )
    }

    change_select_col(value){
        this.props.modify_train_col(this.props.train_key,value);
    }
    change_select_op(value){
        this.props.modify_train_op(this.props.train_key,value);
    }

    change_input_value(e){
        this.props.modify_train_val(this.props.train_key, e.target.value);
    }

    delete_comp(){
        this.props.delete_train_dataset(this.props.train_key);
    }

    render_select_columns() {
        console.log(11189898998);
        let a = 0;
        return (this.state.all_choice_column.map(res => {
            return (<Select.Option key={a++} value={res.name}>{res.verbose_name}</Select.Option>)
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
                    onFocus={this.show_all_name.bind(this)}
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
                    onFocus={this.show_all_name.bind(this)}
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
                    <Select.Option key={1} value="==">==</Select.Option>

                </Select>
            )
        }else{
            return(
                <Select
                value={this.props.op}
                    style={{width: 106}}
                    placeholder="选择运算符"
                    searchPlaceholder="输入"
                    onChange={this.change_select_op.bind(this)}>
                    <Select.Option key={1} value="==">==</Select.Option>
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

export default connect(mapStateToProps,{ get_datasource_columns, delete_train_dataset, modify_train_col, modify_train_op, modify_train_val })(TrainDataset);
