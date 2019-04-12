
import React, { Component } from 'react';
import { Table, Divider, Tag, Pagination, Select, notification, Modal, Menu, Dropdown, Icon, Button, Input } from 'antd';
import '../../node_modules/antd/dist/antd.css'; // 加载antd自带样式
import './valuePermView.less';  // 加载自写样式
import $ from 'jquery';
import axios from 'axios';

const { Column } = Table;
const Option = Select.Option;
const confirm = Modal.confirm;


export default class App extends Component {
    constructor(props) {
        super(props);
        this.state = {
            search: {},
            pageSize: 20,
            page: 1,
            total: 1,
            showTotal: 0,
            allDatasource: [],
            allUser: [],
            allColumn: [],
            allValue: [],
            allShow: [],
            selectedRow: [],
            visible: false,
            confirmLoading: false,
            updateText: {},
            add_form:{
                table_name:'',
                user_name:'',
                col:[],
                val:[]
            },
            add_loading:false,
            add_visible:false
        };
        this.handleChange = this.handleChange.bind(this);
        this.getData = this.getData.bind(this);
        this.changePage = this.changePage.bind(this);
        this.deleteOne = this.deleteOne.bind(this);
        this.deleteSome = this.deleteSome.bind(this);
        this.showEditModal = this.showEditModal.bind(this);
        this.handleOk = this.handleOk.bind(this);
        this.handleCancel = this.handleCancel.bind(this);
        this.getAllColumn = this.getAllColumn.bind(this);
        this.renderOption = this.renderOption.bind(this);
        this.handleBlur = this.handleBlur.bind(this);
        this.handleChangeSelect = this.handleChangeSelect.bind(this);
        this.handleFocus = this.handleFocus.bind(this);
        this.getAllValue = this.getAllValue.bind(this);
        this.renderData = this.renderData.bind(this);
        this.handleChangeData = this.handleChangeData.bind(this);
        this.updateText = this.updateText.bind(this);
        this.renderEditModal = this.renderEditModal.bind(this);
        this.showAddModal = this.showAddModal.bind(this);
        this.handleAddOk = this.handleAddOk.bind(this);
        this.handleAddCancel = this.handleAddCancel.bind(this);
        this.renderAddModal = this.renderAddModal.bind(this);
        // this.edit = this.edit.bind(this);
        // this.deleteOne = this.deleteOne.bind(this);
        // this.onShowSizeChange = this.onShowSizeChange.bind(this);
    }
    // onShowSizeChange(current, pageSize) {
    //     console.log(current, pageSize);
    // }
    //第一次进入页面首先获取默认第一页每页20条的相关数据。
    componentDidMount() {
        this.getData(this.state.search, this.state.page, this.state.pageSize);
    }

    showAddModal(){
        this.setState({
            add_visible:true
        })
    }

    handleAddOk(){
        this.setState({ add_loading:true });
        setTimeout(() => {
            this.setState({ add_loading: false, add_visible: false });
          }, 3000);
    }

    handleAddCancel(){
        this.setState({ add_visible:false });
    }

    showEditModal() {
        this.setState({
            visible: true,
        });
    }
    //打开编辑模态框
    openEditModal(text) {
        this.getAllColumn(text);
        console.log(text);
        text.new_col = text.col;
        text.new_val = text.val;
        this.setState({ updateText: text }, this.setState({ visible: true }))
        // this.setState({
        //     visible: true,
        //     updateText:text
        //   });
    }
    //点击更新模态框的ok按钮
    handleOk() {
        this.setState({
            ModalText: 'The modal will be closed after two seconds',
            confirmLoading: true,
        });
        this.updateText();
        setTimeout(() => {
            this.setState({
                visible: false,
                confirmLoading: false,
            });
        }, 2000);
    }
    //点击更新模态框的cancel按钮
    handleCancel() {
        console.log('Clicked cancel button');
        this.state.updateText.new_col = this.state.updateText.col;
        this.state.updateText.new_val = this.state.updateText.val;
        this.setState({
            visible: false,
            updateText: this.state.updateText
        });
    }
    //改变更新模态框中列的值
    handleChangeSelect(value) {
        console.log(`selected ${value}`);
        this.state.updateText.new_col = value;
        this.state.updateText.new_val= undefined;
        this.setState({updateText:this.state.updateText}, ()=>{this.getAllValue(this.state.updateText)});
      }
      
    handleBlur() {
        console.log('blur');
      }
      
    handleFocus() {
        console.log('focus');
      }
      


    edit(text) {
        console.log(text);
        // console.log(record);
    }
    // 更新
    updateText() {
        const form_data={
            col:this.state.updateText.new_col,
            val:this.state.updateText.new_val
        }
        let ajaxTimeOut = $.ajax({
            type: 'POST',
            url: "/valuepermview/edit/"+this.state.updateText.id+'/',
            data: form_data,
            success: ((data) => {
                console.log(data);
            }),
            error: ((data, type, err) => {
                console.log(data, type, err);
            }),
        })
    }
    // 弹出确定是否删除的确认框
    toChoose(text) {
        const that = this;
        confirm({
            title: '你确定要删除这条数据吗',
            // content: 'Some descriptions',
            okText: 'Yes',
            okType: 'danger',
            cancelText: 'No',
            onOk() {
                console.log('OK');
                that.deleteOne(text);
            },
            onCancel() {
                console.log('Cancel');
            },
        });
    }

    //弹出确定是否删除这些的确认框

    toChooseSome(text) {
        const that = this;
        confirm({
            title: '你确定要删除您选择的这些数据吗',
            // content: 'Some descriptions',
            okText: 'Yes',
            okType: 'danger',
            cancelText: 'No',
            onOk() {
                console.log('OK');
                that.deleteSome(text);
            },
            onCancel() {
                console.log('Cancel');
            },
        });
    }
    //删除一条数据的接口
    deleteOne(text) {
        console.log(text);
        const url = '/valuepermview/delete/' + text.id + '/'
        axios.get(url)
            .then(res => {
                console.log(res);
                if (res.data.msg == "删除成功") {
                    this.getData(this.state.search, this.state.page, this.state.pageSize)
                    notification["success"]({
                        message: '删除成功'
                    });
                }
            })
            .catch(error => {
                console.log(error);
                notification["error"]({
                    message: '删除失败'
                });
            })
    }
    //批量删除数据的接口
    deleteSome() {
        console.log('delete Some');
        const form_data = {
            pks: this.state.selectedRow
        };
        console.log(form_data);
        let ajaxTimeOut = $.ajax({
            type: 'POST',
            url: "/valuepermview/delete/",
            data: form_data,
            success: ((data) => {
                if (data.msg == "删除成功") {
                    this.getData(this.state.search, this.state.page, this.state.pageSize)
                    notification["success"]({
                        message: '删除成功'
                    });
                }
            }),
            error: ((data, type, err) => {
                console.log(data, type, err);
                notification["error"]({
                    message: '删除失败'
                });
            }),
        })
    }
    handleChangeData(value){
        console.log(`selected ${value}`);
        this.state.updateText.new_val = value;
        this.setState({updateText:this.state.updateText});
    }

    handleChange(value) {
        console.log(value);
        this.setState({ pageSize: value }, () => {
            this.getData(this.state.search, this.state.page, this.state.pageSize);
        })

        console.log(this.state.pageSize);
    }

    changePage(pageNumber) {
        console.log('page', pageNumber);
        this.setState({ page: pageNumber }, () => { this.getData(this.state.search, this.state.page, this.state.pageSize) })

    }

    getData(search, page, pageSize) {
        const form_data = {
            search,
            page,
            page_size: pageSize
        };
        let ajaxTimeOut = $.ajax({
            type: 'POST',
            url: "/valuepermview/list/",
            data: form_data,
            success: ((data) => {
                // console.log(data);
                const now_data = data.data
                const new_data = now_data.map((res) => {
                    res.key = res.id
                    return res;
                })
                console.log(new_data);
                const total = Math.ceil(data.total / pageSize) * 10;
                console.log(111, total);
                this.setState({
                    allShow: new_data,
                    total,
                    showTotal: data.total
                })
                console.log(this.state.allShow)
                console.log(this.state.pageSize)
                console.log(this.state.total);
            }),
            error: ((data, type, err) => {
                console.log(data, type, err);
            }),
        })
    }

    getAllUser() {
        axios.get("")
            .then(res => {
                console.log(res);
            })
            .catch(error => {
                console.log(error);
            })
    }

    getAllTable() {
        axios.get("")
            .then(res => {
                console.log(res);
            })
            .catch(error => {
                console.log(error);
            })
    }

    getAllColumn(text) {
        const form_data = {
            pk: text.tab_id
        }
        console.log('form_data', form_data);
        let ajaxTimeOut = $.ajax({
            type: 'POST',
            url: "/valuepermview/table/cols/",
            data: form_data,
            success: ((data) => {
                console.log(data);
                // this.state.updateText.new_col = this.state.updateText.col
                this.setState({allColumn:data})
            }),
            error: ((data, type, err) => {
                console.log(data, type, err);
            }),
        })
    }

    getAllValue(text) {
        console.log('xxxxx',text);
        const form_data = {
            pk: text.tab_id,
            col:text.new_col
        }
        console.log('form_data', form_data);
        let ajaxTimeOut = $.ajax({
            type: 'POST',
            url: "/valuepermview/column/vals/",
            data: form_data,
            success: ((data) => {
                console.log(data);
                this.setState({allValue:data})
            }),
            error: ((data, type, err) => {
                console.log(data, type, err);
            }),
        })
    }

    renderOption(){
        let a = 0
        console.log(11111111,this.state.allColumn);
        return(this.state.allColumn.map((res)=>{
            return(<Select.Option value={res} key={a+1}>{res}</Select.Option>)
        }))
    }

    renderData(){
        let b = 0;
        return(this.state.allValue.map((res)=>{
            return(<Select.Option value={res} key={b+1}>{res}</Select.Option>)
        }))
    }
    // 更新模态框
    renderEditModal(){
        <Modal
                        title="编辑"
                        visible={this.state.visible}
                        onOk={this.handleOk}
                        confirmLoading={this.state.confirmLoading}
                        onCancel={this.handleCancel}
                    >
                        <div>
                            <span>表名:</span>
                            <Input value={this.state.updateText.verbose_name} disabled />
                        </div>
                        <div>
                            <span>用户名:</span>
                            <Input value={this.state.updateText.username} disabled />
                            {/* <span>{this.state.updateText.username}</span> */}
                        </div>
                        <div>
                            <span>字段名:</span>
                            <Select
                                showSearch
                                style={{ width: 200 }}
                                placeholder="Select a person"
                                optionFilterProp="children"
                                onChange={this.handleChangeSelect}
                                onFocus={this.handleFocus}
                                onBlur={this.handleBlur}
                                value = {this.state.updateText.new_col}
                                filterOption={(input, option) => option.props.children.toLowerCase().indexOf(input.toLowerCase()) >= 0}
                            >
                                {this.renderOption()}
                            </Select>
                        </div>
                        <div>
                            <span>字段值:</span>
                            <Select
                            mode="multiple"
                            style={{ width: '100%' }}
                            placeholder="Please select"
                            value={this.state.updateText.new_val}
                            onChange={this.handleChangeData}
                        >
                            {this.renderData()}
                        </Select>
                        </div>
                    </Modal>
    }

    renderAddModal(){
        <Modal
          visible={this.state.add_visible}
          title="增加新纪录"
          onOk={this.handleAddOk}
          onCancel={this.handleAddCancel}
          footer={[
            <Button key="back" onClick={this.handleAddCancel}>Return</Button>,
            <Button key="submit" type="primary" loading={this.state.add_loading} onClick={this.handleAddOk}>
              Submit
            </Button>,
          ]}
        >
          <p>Some contents...</p>
          <p>Some contents...</p>
          <p>Some contents...</p>
          <p>Some contents...</p>
          <p>Some contents...</p>
        </Modal>
    }

    render() {
        const rowSelection = {
            onChange: (selectedRowKeys, selectedRows) => {
                console.log(`selectedRowKeys: ${selectedRowKeys}`, 'selectedRows: ', selectedRows);
                this.setState({ selectedRow: selectedRowKeys }, () => {
                    console.log(111, this.state.selectedRow)
                });
            },
            getCheckboxProps: record => ({
                disabled: record.name === 'Disabled User', // Column configuration not to be checked
                name: record.name,
            }),
        };
        const menu = (
            <Menu>
                <Menu.Item key="0">
                    <a onClick={this.toChooseSome.bind(this)}>删除</a>
                </Menu.Item>
            </Menu>
        )
        return (
            <div className="container">
                        <Icon type="plus-circle" theme="twoTone" twoToneColor="#eb2f96" />
                        <button onClick={this.showAddModal}>111</button>
                <Select defaultValue={this.state.pageSize} style={{ width: 120 }} onChange={this.handleChange}>
                    <Option value={20}>20条/页</Option>
                    <Option value={50}>50条/页</Option>
                    <Option value={75}>75条/页</Option>
                    <Option value={100}>100条/页</Option>
                </Select>
                <Table dataSource={this.state.allShow} pagination={false} scroll={{ y: 600 }} rowSelection={rowSelection}>
                    <Column
                        title="表"
                        dataIndex="table_name"
                        key="table_name"
                        width={350}
                    />
                    <Column
                        title="表名"
                        dataIndex="verbose_name"
                        key="verbose_name"
                        width={150}
                    />
                    <Column
                        title="用户名"
                        dataIndex="username"
                        key="username"
                        width={150}
                    />
                    <Column
                        title="字段名"
                        dataIndex="col"
                        key="col"
                        width={150}
                    />
                    <Column
                        title="字段值"
                        dataIndex="val"
                        key="val"
                        width={150}
                    />
                    <Column
                        title="添加人"
                        dataIndex="creator"
                        key="creator"
                        width={150}
                    />
                    <Column
                        title="修改时间"
                        dataIndex="modify"
                        key="modify"
                        width={150}
                    />
                    <Column
                        title="操作"
                        key="action"
                        width={250}
                        render={(text, record) => (
                            <span>
                                <Tag color='blue' onClick={this.openEditModal.bind(this, text)}>编辑</Tag>
                                <Divider type="vertical" />
                                <Tag color='red' onClick={this.toChoose.bind(this, text)}>删除</Tag>
                            </span>
                        )}
                    />
                </Table>
                <Pagination
                    showTotal={(total) => <strong>记录数:{this.state.showTotal}</strong>}
                    total={this.state.total}
                    onChange={this.changePage}
                    hideOnSinglePage={true}

                />
                <Dropdown overlay={menu} trigger={['click']}>
                    <a className="ant-dropdown-link" href="#">
                        操作<Icon type="down" />
                    </a>
                </Dropdown>
                <div>
                    {this.renderEditModal()}
                </div>
                <div>
                    {this.renderAddModal()}
                </div>
            </div>
        );
    }
}
