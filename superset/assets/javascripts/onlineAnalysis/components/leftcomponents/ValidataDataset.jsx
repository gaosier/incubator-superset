import React, {Component} from 'react';
import { connect } from 'react-redux';
import { Button, Input, Select } from 'antd';
import ValidataFilter from '../leftcomponents/ValidataFilter';
import {add_val_filter,delete_validate_datasets,modify_name} from '../../actions/leftmenu';

class ValidataDataset extends Component {
    constructor(props){
        super(props);
    }
    change_input_name(e){
        this.props.modify_name(this.props.val_key,e.target.value);
    }
    increase_model(){
        this.props.add_val_filter(this.props.val_key);
    }
    delete_valdata(){
        this.props.delete_validate_datasets(this.props.val_key);
    }
    render_show_name(){
        if(this.props.name===''){
            return(
                <div>
                <Input
                    value={undefined}
                    placeholder="请定义验证集名称"
                    onChange={this.change_input_name.bind(this)}
                />
                <button id="remove-button"
                                type="button"
                                className="btn btn-sm btn-default"
                                onClick={this.delete_valdata.bind(this)}
                        >
                            <i className="fa fa-minus"></i></button>
                </div>
            )
        }else{
            return(
                <div>
                <Input
                    value={this.props.name}
                    placeholder="请定义验证集名称"
                    onChange={this.change_input_name.bind(this)}
                />
                    <button id="remove-button"
                                type="button"
                                className="btn btn-sm btn-default"
                                onClick={this.delete_valdata.bind(this)}
                        >
                            <i className="fa fa-minus"></i></button>
                </div>
            )
        }
    }

    render_filter(){
        return(this.props.leftmenu.form_data.validate_datasets[this.props.val_key].filters.map((dum,index) =>(
            <ValidataFilter
                col={dum.col}
                op={dum.op}
                val={dum.val}
                filter_key={index}
                key={index}
                val_key={this.props.val_key}
            />
        )))
    }



    render() {
        return (
            <div>
                <div className="space-1 row">
                    <div className="col-md-12">
                        {this.render_show_name()}
                    </div>
                </div>
                {this.render_filter()}
                <button id="add-button"
                        type="button"
                        className="btn btn-sm btn-default"
                        onClick={this.increase_model.bind(this)}
                >
                    <i className="fa fa-plus"></i>增加验证模型数据集
                </button>

            </div>
        );
    }
}

const mapStateToProps = (state) => {
    return {
        leftmenu: state.leftmenu,
    }
};

export default connect(mapStateToProps,{ add_val_filter,delete_validate_datasets,modify_name })(ValidataDataset);
