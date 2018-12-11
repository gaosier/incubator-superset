import React, {Component} from 'react';
import {connect} from "react-redux";
import {Modal, Table} from 'react-bootstrap';
import {
    get_all_dealna,
    set_null_operation,
    set_variable_box,
    increase_dummy,
    increament_correlation, getcode, get_alldealna, see_corr
} from '../../actions/leftmenu';
import Variablebox from '../leftcomponents/Variablebox';
import Dummy from '../leftcomponents/Dummy';
import {Select, Radio, Button, Divider, Icon, notification} from 'antd';
import CorrelationAnalysis from '../leftcomponents/CorrelationAnalysis';
import axios from 'axios';
import {t} from "../../../locales";

const RadioGroup = Radio.Group;

class DescriptiveAnalysis extends Component {
    constructor(props) {
        super(props);
        this.state = {
            showModal: false,
            show_describeModal: false,
            loading: true,
            variable_box: [],
            show_input: false,
            operate: true,
            value: '',
            detail: {},
            describe_table: '',
        };
        this.openModal = this.openModal.bind(this);
        this.toggleModal = this.toggleModal.bind(this);
        this.enterModal = this.enterModal.bind(this);
        this.onChange = this.onChange.bind(this);
        this.save_null_operate = this.save_null_operate.bind(this);
        this.change_value = this.change_value.bind(this);
        this.toggle_descModal = this.toggle_descModal.bind(this);
    }

    save_null_operate() {
        if (this.state.value === 'fill') {
            let detail = [];
            for (var i = 0; i < Object.keys(this.state.detail).length; i++) {
                detail.push([Object.keys(this.state.detail)[i], Object.values(this.state.detail)[i]]);
            }
            this.props.set_null_operation(this.state.value, detail)
        } else {
            console.log('xxxx', this.state.value);
            this.props.set_null_operation(this.state.value, [])
        }
        this.setState({
            showModal: !this.state.showModal,
            value: '',
            detail: {}
        })
    }

    openModal() {
        this.props.get_all_dealna(this.props.leftmenu.form_data.sk_type, this.props.leftmenu.datasource_id);
        this.setState({showModal: !this.state.showModal});
    }

    toggleModal() {
        this.setState({showModal: !this.state.showModal});
    }

    toggle_descModal() {
        this.setState({show_describeModal: !this.state.show_describeModal})
    }

    enterModal() {
        this.setState({showModal: !this.state.showModal});
    }

    onChange(e) {
        this.setState({
            value: e.target.value,
        });
        if (e.target.value === 'fill') {
            this.setState({
                operate: false
            })
        } else {
            this.setState({
                operate: true
            })
        }
    };

    change_value(value, operation) {
        let column = {};
        column[operation.key] = value;
        this.setState({
            detail: Object.assign(this.state.detail, column)
        });
    }

    increament_variable_box() {
        this.props.set_variable_box();
    }

    increament_dummy() {
        this.props.increase_dummy();
    }

    increament_correlation_analysis() {
        this.props.increament_correlation();
    }

    watch_describe() {
        this.setState({
            show_describeModal: true
        });
        const form_data = {
            datasource: this.props.leftmenu.form_data.datasource,
            sk_type: this.props.leftmenu.form_data.sk_type
        };
        $.ajax({
            type: 'POST',
            url: "/online/describe/",
            data: {
                form_data: JSON.stringify(form_data),
            },
            dataType: "TEXT",
            success: ((data) => {
                console.log(111, data);
                this.setState({
                    loading: false,
                    describe_table: data
                })
            }),
            error: ((data, type, err) => {
                console.log(222, data, type, err);
                notification['error']({
                    message: '获取缺失值失败',
                    description: '获取缺失值必须选择模型名称,您可能未选择模型名,若您已选择,请咨询相关人员.',
                });
            }),
        })
    }

    download_data() {
        // axios.post('/path/to/download/url', this.searchParams, {
        //   responseType: 'blob'
        // }).then(res => {
        //   let blob = res.data;
        //   let reader = new FileReader();
        //   reader.readAsDataURL(blob);
        //   reader.onload = (e) => {
        //     let a = document.createElement('a');
        //     a.download = `表格名称.xlsx`;
        //     a.href = e.target.result;
        //     document.body.appendChild(a);
        //     a.click()
        //     document.body.removeChild(a)
        //   }
        // }).catch(err => {
        //   console.log(err.message)
        // })
        console.log(1111, this.props.leftmenu.form_data);
        const form_data = {
            datasource: this.props.leftmenu.form_data.datasource,
            version: this.props.leftmenu.form_data.version,
            sk_type: this.props.leftmenu.form_data.sk_type,
            analysis_id: this.props.leftmenu.form_data.analysis_id,
            analysis_name: this.props.leftmenu.form_data.analysis_name,
            null_operate: this.props.leftmenu.form_data.null_operate,
            variable_box: this.props.leftmenu.form_data.variable_box,
            dummy_variable: this.props.leftmenu.form_data.dummy_variable
        }
        console.log(222, form_data);

        // $.ajax({
        //     type: "POST",
        //     url: "/online/download/",
        //     data: {
        //         form_data: JSON.stringify(form_data),
        //     },
        const exploreForm = document.createElement('form');
          exploreForm.action = "/online/download/";
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


    render_correlation_analysis() {
        return (this.props.leftmenu.form_data.correlation_analysis.map((dum, index) => (
            <CorrelationAnalysis
                field={dum[0]}
                handle_props={dum[1]}
                handle_type={dum[2]}
                key={index}
                correlation_key={index}
            />
        )))
    }

    render_variable_box() {
        if (this.props.leftmenu.form_data.variable_box === []) {

        } else {
            this.setState({comps: this.props.leftmenu.form_data.variable_box})
        }
    }

    render_dummy() {
        return (this.props.leftmenu.form_data.dummy_variable.map((dum, index) => (
            <Dummy
                field={dum.field}
                labels={dum.labels}
                key={index}
                dummy_key={index}
            />
        )))
    }

    render_variable() {
        return (this.props.leftmenu.form_data.variable_box.map((comp, index) => (
            <Variablebox
                field={comp.field}
                bins={comp.bins}
                labels={comp.labels}
                variable_key={index}
                key={index}
            />
        )))
    }

    render_dealina() {
        const keys = Object.keys(this.props.leftmenu.all_dealina);
        return keys.map(key => (

            <tr>
                <td>
                    {key}
                </td>
                <td>
                    {this.props.leftmenu.all_dealina[key]}
                </td>
                <td>
                    <Select
                        disabled={this.state.operate}
                        defaultValue="请选择填充值"
                        showSearch style={{width: 200}}
                        searchPlaceholder="输入"
                        onChange={this.change_value.bind(this)}
                    >
                        <Select.Option key={key} value="median">median</Select.Option>
                        <Select.Option key={key} value="mode">mode</Select.Option>
                        <Select.Option key={key} value="mean">mean</Select.Option>
                        <Select.Option key={key} value="0">0</Select.Option>
                    </Select>
                </td>
            </tr>)
        );
    }

    render_desc_Modal() {
        return (
            <Modal
                show={this.state.show_describeModal}
                onHide={this.toggle_descModal}
                bsSize="lg">
                <Modal.Header closeButton>
                    <Modal.Title>查看数据分布</Modal.Title>
                </Modal.Header>
                <Modal.Body>
                    {this.state.loading &&
                    <img
                        className="loading"
                        alt="Loading..."
                        src="../../../../../static/assets/images/loading.gif"
                    />
                    }
                    {<div dangerouslySetInnerHTML={{__html: this.state.describe_table}}/>}
                </Modal.Body>
                <Modal.Footer>
                    <Button onClick={this.toggle_descModal}>关闭</Button>
                </Modal.Footer>
            </Modal>

        )
    }

    renderModal() {

        return (
            <Modal
                show={this.state.showModal}
                onHide={this.toggleModal}
                bsSize="lg"
            >

                <Modal.Header closeButton>
                    <Modal.Title>缺失值处理</Modal.Title>
                </Modal.Header>
                <Modal.Body>
                    <div><span>操作</span>
                        <RadioGroup onChange={this.onChange} value={this.state.value}>
                            <Radio value="fill">填充</Radio>
                            <Radio value="delete">删除</Radio>
                        </RadioGroup>
                    </div>
                    <Table>
                        <thead>
                        <tr>
                            <th>
                                列名
                            </th>
                            <th>
                                缺失值数量
                            </th>
                            <th>
                                填充值
                            </th>
                        </tr>
                        </thead>
                        <tbody>
                        {this.render_dealina()}
                        </tbody>
                    </Table>
                </Modal.Body>
                <Modal.Footer>
                    <Button onClick={this.enterModal}>关闭</Button>
                    <Button onClick={this.save_null_operate}>保存</Button>
                </Modal.Footer>
            </Modal>
        )
    }

    render() {
        const {variable_box} = this.state;
        var a = 0;
        return (
            <div>

                <div>
                    <Divider>数据分布</Divider>
                    <Button onClick={this.watch_describe.bind(this)}><Icon type="search"/>查看数据分布</Button>
                </div>
                {this.render_desc_Modal()}
                <div>
                    <Divider>缺失值处理</Divider>
                    <Button onClick={this.openModal}><Icon type="zoom-in"/>缺失值处理</Button>
                </div>
                {this.renderModal()}
                <div>
                    <Divider>变量分箱</Divider>
                    <br/>
                    <div>
                        {this.render_variable()}
                        <Button onClick={this.increament_variable_box.bind(this)}><Icon type="plus"/>增加变量分箱条件</Button>
                    </div>
                </div>
                <div>
                    <Divider>哑变量处理</Divider>
                    <div>
                        {this.render_dummy()}
                        <Button onClick={this.increament_dummy.bind(this)}><Icon type="plus"/>增加哑变量处理条件</Button>
                    </div>
                </div>
                <div>
                    <Divider>相关性分析</Divider>
                    <div>
                        {this.render_correlation_analysis()}
                        <Button onClick={this.increament_correlation_analysis.bind(this)}><Icon type="plus"/>增加变量相关性分析条件</Button>
                        <Button><Icon type="search"/>查看变量相关性</Button>
                    </div>
                </div>

                <div>
                    <Divider>下载数据</Divider>
                    <a
                      onClick={this.download_data.bind(this)}
                      target="_blank"
                    >
                       <i className="fa fa-file-text-o" />下载数据
                    </a>
                    {/*<Button onClick={this.download_data.bind(this)}><Icon type="download"/>下载数据</Button>*/}
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
    get_all_dealna,
    set_null_operation,
    set_variable_box,
    increase_dummy,
    increament_correlation
})(DescriptiveAnalysis);
