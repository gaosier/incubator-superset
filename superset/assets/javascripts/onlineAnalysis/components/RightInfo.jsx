import React, {Component} from 'react'
import {Tabs, Tab} from 'react-bootstrap';
import { Button } from 'antd';
import {connect} from 'react-redux';
import axios from 'axios';

class RightInfo extends Component {
    constructor(props) {
        super(props);
        this.state = {
            log: '',
            img: [],
            param: ''
        };
        this.get_info = this.get_info.bind(this);
        this.get_img = this.get_img.bind(this);
        this.get_param = this.get_param.bind(this);
    }

    componentDidMount() {
        this.get_info('code', this.props.log_dir_id);
        this.get_img('image', this.props.log_dir_id);
        this.get_param('param', this.props.log_dir_id);
    }

    componentWillReceiveProps(nextProps) {
        console.log(11111, nextProps);
        if (this.props.log_dir_id === nextProps.log_dir_id) {
            console.log('相等')
        } else {
            console.log('不想等');
            this.get_info('code', this.props.log_dir_id);
            this.get_img('image', this.props.log_dir_id);
            this.get_param('param', this.props.log_dir_id);
        }
    }

    get_info(name, id) {
        axios.get('/online/log/' + name + '/?log_dir_id=' + id)
            .then(res => {
                console.log('log',res);
                // const data = res.data.replace(/\r\n/g,'<br>');
                // console.log('data',data);
                this.setState({
                    log: res.data
                })
            })
            .catch(error => {
            })
        // return(<div><div>1</div><div>{this.state.log}</div></div>)
    }

    get_param(name, id) {
        axios.get('/online/log/' + name + '/?log_dir_id=' + id)
            .then(res => {
                console.log('param', res);
                this.setState({
                    param: res.data
                })
            })
            .catch(error => {
            })
    }

    get_img(name, id) {
        axios.get('/online/log/' + name + '/?log_dir_id=' + id)
            .then(res => {
                console.log('image', res);
                this.setState({
                    img: res.data
                })
            })
            .catch(error => {
            })
    }

    render_log() {
        // if(this.props.leftmenu.run_load === true){
        //     this.setState({
        //         log:!this.state.log
        //     });
        //     return(
        //     <img
        //                   className="loading"
        //                   alt="Loading..."
        //                   src="../../../../static/assets/images/loading.gif"
        //                 />)
        // }

        // if(this.props.log_dir_id === ''){
        //     return(<div>暂时不存在值</div>)
        //
        // }else{

        // }
        // return(<div dangerouslySetInnerHTML={{__html: this.state.log}}/>)
        return (<pre>{this.state.log}</pre>)
    }

    render_img() {
        // if (this.props.leftmenu.run_load === true) {
        //     return (
        //         <img
        //             className="loading"
        //             alt="Loading..."
        //             src="../../../../static/assets/images/loading.gif"
        //         />)
        // }
        //     if(this.props.leftmenu.form_data.log_dir_id === ''){
        //         return(<div>暂时不存在值</div>)
        //
        //     }else{
        //         if(this.props.rightinfo.image ===[]){
        //             this.props.get_log('param',this.props.leftmenu.form_data.log_dir_id);
        //         }
        //         return(<div>{ this.props.rightinfo.image }</div>)
        //     }
        //
        // return (<div>{this.state.img}</div>)
        return(this.state.img.map((dun,index) =>{
             const url_img = "/static/uploads/img/" + dun;
            return(<div key={index}><img src={url_img} /></div>)
        }))
    }

    render_to_leader() {
            // if(this.props.leftmenu.run_load === true){
            //     return(
            //     <img
            //                   className="loading"
            //                   alt="Loading..."
            //                   src="../../../../static/assets/images/loading.gif"
            //                 />)
            // }
        //     if(this.props.leftmenu.form_data.log_dir_id === ''){
        //         return(<div>暂时不存在值</div>)
        //
        //     }else{
        //         if(this.props.rightinfo.show ===[]){
        //             this.props.get_log('image',this.props.leftmenu.form_data.log_dir_id);
        //         }
        //         return(<div>{ this.props.rightinfo.show }</div>)
        //     }
        return (<pre>{this.state.param}</pre>)
    }
    download_data(){
        const form_data = {
            model_result_execl_sl: this.props.leftmenu.form_data.model_result_execl_sl,
        };
        const exploreForm = document.createElement('form');
        exploreForm.action = "/online/model/complete/download/";
        exploreForm.method = 'POST';
        exploreForm.target = '_blank';
        const token = document.createElement('input');
        token.type = 'hidden';
        token.name = 'csrf_token';
        token.value = (document.getElementById('csrf_token') || {}).value;
        exploreForm.appendChild(token);
        const data = document.createElement('input');
        data.type = 'hidden';
        data.name = 'form_data';
        data.value = JSON.stringify(form_data);
        exploreForm.appendChild(data);

        document.body.appendChild(exploreForm);
        exploreForm.submit();
        document.body.removeChild(exploreForm);
    }

    // download_leader(){
    //     const form_data = {
    //         model_result_execl_bs: this.props.leftmenu.form_data.model_result_execl_bs,
    //     };
    //     const disForm = document.createElement('form');
    //     disForm.action = "/online/model/complete/download/";
    //     disForm.method = 'POST';
    //     disForm.target = '_blank';
    //     const token = document.createElement('input');
    //     token.type = 'hidden';
    //     token.name = 'csrf_token';
    //     token.value = (document.getElementById('csrf_token') || {}).value;
    //     disForm.appendChild(token);
    //     const data = document.createElement('input');
    //     data.type = 'hidden';
    //     data.name = 'form_data';
    //     data.value = JSON.stringify(form_data);
    //     disForm.appendChild(data);
    //
    //     document.body.appendChild(disForm);
    //     disForm.submit();
    //     document.body.removeChild(disForm);
    // }

    render() {
        return (
            <div>
                <div id="down_load">
                <Button id="download_data">
                        <a
                            onClick={this.download_data.bind(this)}
                            target="_blank"
                        >
                            <i className="fa fa-file-text-o"/>下载数据分析师文件
                        </a>
                    </Button>
                 {/*<Button id="download_leader">*/}
                        {/*<a*/}
                            {/*onClick={this.download_leader.bind(this)}*/}
                            {/*target="_blank"*/}
                        {/*>*/}
                            {/*<i className="fa fa-file-text-o"/>下载业务方展示文件*/}
                        {/*</a>*/}
                    {/*</Button>*/}
                </div>
                <Tabs defaultActiveKey={1} id="uncontrolled-tab-example">
                    <Tab eventKey={1} title={"代码日志展示"}>
                        {/*{ this.get_info('code',this.props.log_dir_id)}*/}
                        {this.render_log()}
                    </Tab>
                    <Tab eventKey={2} title={"参数日志展示"}>
                        {this.render_to_leader()}
                    </Tab>
                    <Tab eventKey={3} title={"图片日志展示"}>
                        {this.render_img()}
                    </Tab>
                </Tabs>
            </div>
        )
    }
}

const mapStateToProps = (state) => {
    return {
        leftmenu: state.leftmenu,
        rightinfo: state.rightinfo
    }
};

export default connect(mapStateToProps, {})(RightInfo);
