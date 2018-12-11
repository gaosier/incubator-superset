import React, {Component} from 'react';
import {Select, Input} from 'antd';
import {connect} from "react-redux";
import {
    get_datasource_columns,
    delete_variable_box,
    modify_variable_box_field,
    modify_variable_box_bins,
    modify_variable_box_labels
} from '../../actions/leftmenu';
import axios from 'axios';

class Variablebox extends Component {
    constructor(props) {
        super(props);
        console.log('index', props);
        this.state={
            all_choice_column:[]
        }
    }

    render_select() {
        console.log(111);
        let a = 0;
        return (this.state.all_choice_column.map(res => {
            return (<Select.Option key={a++} value={res.name}>{res.verbose_name}</Select.Option>)
        }))

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

    // componentDidMount() {
    //     this.props.get_datasource_columns(this.props.leftmenu.datasource_id);
    // }

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
                            onFocus={this.show_all_name.bind(this)}
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
                            placeholder="请选择要进行变量分箱的列"
                            onFocus={this.show_all_name.bind(this)}
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
        console.log(e.target.value);
        this.props.modify_variable_box_bins(this.props.variable_key, e.target.value);
    }

    change_labels(e) {
        console.log(e.target.value);
        this.props.modify_variable_box_labels(this.props.variable_key, e.target.value);
    }

    render_input_bins() {
        if (this.props.bins === '') {
            return (
                <div className="col-md-5">
                    <Input
                        value={undefined}
                        placeholder="范围:[0,100,200,300]"
                        onChange={this.change_bins.bind(this)}
                    />
                </div>
            )
        } else {
            return (
                <div className="col-md-5">
                    <Input
                        placeholder="范围:[0,100,200,300]"
                        value={this.props.bins}
                        onChange={this.change_bins.bind(this)}
                    />
                </div>
            )
        }
    }

    render_input_lables() {
        if (this.props.labels === '') {
            return (
                <div className="col-md-5">
                    <Input
                        value={undefined}
                        placeholder="替换值:[0,1,2,3]"
                        onChange={this.change_labels.bind(this)}
                    />
                </div>
            )
        } else {
            return (
                <div className="col-md-5">
                    <Input
                        value={this.props.labels}
                        placeholder="替换值:[0,1,2,3]"
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
                    {this.render_input_lables()}
                    <div className="col-md-2">
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
    modify_variable_box_labels
})(Variablebox);
