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

class CorrelationAnalysis extends Component {
    constructor(props) {
        super(props);
        this.state={
            matplob:false,
            seaborn:false,
        }}



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
        if(value==='seaborn'){
            this.setState({
                matplob:false,
                seaborn:true,
            })
        }else{
            this.setState({
                matplob:true,
                seaborn:false,
            })
        }
        this.props.modify_correlation_two(this.props.correlation_key, value);
    }

    render_select() {
        return (this.props.leftmenu.slice.all_select_column.map((res,index) => {
            return (<Select.Option key={index} value={res.name}>{res.verbose_name}</Select.Option>)
        }))
    }

    render_draw_props() {
        if (this.props.handle_props === 0) {
            return (
                <Select
                    value={undefined}
                    style={{width: 106}}
                    placeholder="请选择方法"
                    showSearch
                    searchPlaceholder="输入"
                    onChange={this.change_select_props.bind(this)}
                >
                    <Select.Option key={1} value="matplotlib">matplotlib</Select.Option>
                    <Select.Option key={2} value="seaborn">seaborn</Select.Option>

                </Select>
            )
        } else {
            return (
                <Select
                    style={{width: 106}}
                    value={this.props.handle_props}
                    showSearch
                    placeholder="请选择方法"
                    searchPlaceholder="输入"
                    onChange={this.change_select_props.bind(this)}
                >
                    <Select.Option key={1} value="matplotlib">matplotlib</Select.Option>
                    <Select.Option key={2} value="seaborn">seaborn</Select.Option>

                </Select>
            )
        }
    }

    render_value(){
        const a = ['line','bar','barh','hist','box','kde','density','area','pie','scatter','hexbin'];
        const b = ['boxplot','violinplot','striplot','swarmplot','barplot','countplot','factorplot','heatmap'];
        if(this.state.matplob){
            return (a.map((res,index) => {
                return (<Select.Option key={index} value={res}>{res}</Select.Option>)
            }))
        }else if(this.state.seaborn){
             return (b.map((res,index) => {
                return (<Select.Option key={index} value={res}>{res}</Select.Option>)
            }))
        }else{

        }
    }


    render_draw_type() {
        if (this.props.handle_type === 0) {
            return (
                <Select
                    value={undefined}
                    style={{width: 270}}
                    showSearch
                    placeholder="请选择类型"
                    searchPlaceholder="输入"
                    onChange={this.change_select_type.bind(this)}
                >
                    {this.render_value()}


                </Select>
            )
        } else {
            return (
                <Select
                    style={{width: 270}}
                    value={this.props.handle_type}
                    showSearch
                    placeholder="请选择类型"
                    searchPlaceholder="输入"
                    onChange={this.change_select_type.bind(this)}
                >
                    {this.render_value()}
                </Select>
            )
        }
    }

    render_select_columns() {
        if (this.props.field === 0) {
            return (
                <Select
                    value={undefined}
                    mode="multiple"
                    style={{width: 484}}
                    placeholder="请选择列名"
                    showSearch
                    searchPlaceholder="输入"
                    onChange={this.change_select.bind(this)}
                >
                    {this.render_select()}
                </Select>
            )
        } else {
            return (
                <Select
                    style={{width: 484}}
                    mode="multiple"
                    value={this.props.field}
                    showSearch
                    placeholder="请选择列名"
                    searchPlaceholder="输入"
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
