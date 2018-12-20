import React, { Component } from 'react'
import axios from 'axios';
import { notification, Button } from 'antd';
import './main.css';

class ShowResult extends Component {
    constructor(props){
        super(props);
        this.state={
            show:''
        }
    }

    componentDidMount(){
        const url = window.location.href.split('/');
        console.log(url[url.length -1]);
        axios.get('/online/log/business/?log_dir_id='+url[url.length -1])
            .then(res => {
                console.log(res);
                this.setState({
                    show:res.data
                })
            })
            .catch(error => {
                notification['error']({
                    message: '获取日志失败',
                    description: '详情请咨询相关人员.',
                });
            })
    }

    download_data(){
        const form_data = {
            model_result_execl_bs: this.props.data,
        };
        const disForm = document.createElement('form');
        disForm.action = "/online/model/complete/download/";
        disForm.method = 'GET';
        disForm.target = '_blank';
        const token = document.createElement('input');
        token.type = 'hidden';
        token.name = 'csrf_token';
        token.value = (document.getElementById('csrf_token') || {}).value;
        disForm.appendChild(token);
        const data = document.createElement('input');
        data.type = 'hidden';
        data.name = 'form_data';
        data.value = JSON.stringify(form_data);
        disForm.appendChild(data);

        document.body.appendChild(disForm);
        disForm.submit();
        document.body.removeChild(disForm);
    }

    render_img(){
        return(<pre>{this.state.show}</pre>)
    }

    render() {
        return (
            <div>
                <div id="download">
                <Button>
                        <a
                            onClick={this.download_data.bind(this)}
                            target="_blank"
                        >
                            <i className="fa fa-file-text-o"/>下载数据
                        </a>
                    </Button>
                </div>
                <div id="zhanshi">
                    {this.render_img()}
                </div>
            </div>
        )
    }
}

export default ShowResult;
