import React, { Component } from 'react'
import { Tabs, Tab } from 'react-bootstrap';
import { connect } from 'react-redux';
import { get_log } from '../actions/rightinfo';

class RightInfo extends Component {
    constructor(props){
        super(props);
    }
    render_log(){
        if(this.props.leftmenu.form_data.log_dir_id === ''){
            return(<div>暂时不存在值</div>)

        }else{
            if(this.props.rightinfo.log ===[]){
                this.props.get_log('code',this.props.leftmenu.form_data.log_dir_id);
            }
            return(<p>{ this.props.rightinfo.log }</p>)
        }

    }
    render_img(){

        if(this.props.leftmenu.form_data.log_dir_id === ''){
            return(<div>暂时不存在值</div>)

        }else{
            if(this.props.rightinfo.image ===[]){
                this.props.get_log('param',this.props.leftmenu.form_data.log_dir_id);
            }
            return(<p>{ this.props.rightinfo.image }</p>)
        }

    }
    render_to_leader(){
        if(this.props.leftmenu.form_data.log_dir_id === ''){
            return(<div>暂时不存在值</div>)

        }else{
            if(this.props.rightinfo.show ===[]){
                this.props.get_log('image',this.props.leftmenu.form_data.log_dir_id);
            }
            return(<p>{ this.props.rightinfo.show }</p>)
        }
    }
    render() {
        return (
            <div>
                <Tabs defaultActiveKey={1} id="uncontrolled-tab-example" >
                    <Tab eventKey={1} title={"日志展示"}>
                        { this.render_log() }
                    </Tab>
                    <Tab eventKey={2} title={"图表展示"}>
                        { this.render_img() }
                    </Tab>
                    <Tab eventKey={3} title={"业务方数据展示"}>
                        {this.render_to_leader()}
                    </Tab>
                </Tabs>
            </div>
        )
    }
}
const mapStateToProps = (state) => {
    return {
        leftmenu: state.leftmenu,
        rightinfo:state.rightinfo
    }
};

export default connect(mapStateToProps,{ get_log })(RightInfo);
