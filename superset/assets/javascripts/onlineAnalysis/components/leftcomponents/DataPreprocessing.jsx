import React, {Component} from 'react';
import {
    Upload, message, Button, Icon,
} from 'antd';
import $ from "jquery";
import {connect} from 'react-redux';
import {set_description_img} from '../../actions/leftmenu';
import {Modal} from 'react-bootstrap';


class DataPreprocessing extends Component {
    constructor(props) {
        super(props);
        this.state = {
            show_Modal: false,
            fileList: [],
        };
        this.toggleModal = this.toggleModal.bind(this);
        this.handleChange = this.handleChange.bind(this);
    }

    toggleModal() {
        this.setState({show_Modal: !this.state.show_Modal});
    }

    onEnterModal() {
        if (this.props.leftmenu.form_data.description_img === "") {
            return (
                <div>没有上传图片或上传图片不成功,请重新上传</div>)
        } else {
            const url_img = "/static/uploads/img/" + this.props.leftmenu.form_data.description_img;
            return (
                <div>
                    <img src={url_img}/>
                </div>
            )
        }
    }

    handleChange(info) {
        if (info.file.status !== 'uploading') {
            this.props.set_description_img(info.file.response.filename);

        }
        if (info.file.status === 'done') {
            message.success("图片上传成功");
        } else if (info.file.status === 'error') {
            message.error(`图片上传失败`);
        }
        let fileList = info.fileList;
        fileList = fileList.slice(-1);
        this.setState({fileList});
    }

    render_modal() {
        return (
            <Modal
                show={this.state.show_Modal}
                onHide={this.toggleModal}
                bsSize="lg">
                <Modal.Header closeButton>
                    <Modal.Title>描述分析图片展示</Modal.Title>
                </Modal.Header>
                <Modal.Body id="miaoshufenxi">
                    {this.onEnterModal()}
                </Modal.Body>

            </Modal>)

    }

    upload(file, fileList) {
        console.log(file, fileList);
        const File = [{
            uid: '1',
            name: fileList.name,
            statue: 'done'
        }];
        this.setState({
            fileList: File
        })
    }

    render() {
        const token = $('input#csrf_token').val();
        const props = {
            action: '/online/upload/file/',
            withCredentials: true,
            headers: {
                authorization: 'authorization-text',
                "X-CSRFToken": token,
            },
            directory: false,
            onChange: this.handleChange,
        };

        return (
            <div>
                <div>
                    <Upload {...props} fileList={this.state.fileList}>
                        <Button>
                            <Icon type="upload"/> 上传图片
                        </Button>
                    </Upload>
                </div>
                <div id="watch-img">
                    <Button onClick={this.toggleModal}>
                        <Icon type="zoom-in"/> 查看图片
                    </Button>
                    {this.render_modal()}
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
export default connect(mapStateToProps, {set_description_img})(DataPreprocessing);
