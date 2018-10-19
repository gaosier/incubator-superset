import $ from 'jquery';

import '../../node_modules/antd/dist/antd.css'; // 加载antd自带样式
import { Tree } from 'antd';
import React, { Component } from 'react';
import './datacenter.less';  // 加载自写样式
import Info from './Info';  // 右侧列表组件



const TreeNode = Tree.TreeNode;
export default class App extends Component {
    constructor(props) {
        super(props);
        this.state = {
            treeData: [], //存放初始化加载的菜单内容，即第一层级菜单内容
            TreeNodeData: [], //存放获取的子菜单内容
            infos: [], //存放右侧数据
            title: '用户数据中心', //存放右侧数据title
        };
        this.onLoadData = this.onLoadData.bind(this);
        this.onSelect = this.onSelect.bind(this);
        this.renderTreeNodes = this.renderTreeNodes.bind(this);
    }
    // 通过id获取第一层层级关系
    getKnowledgeStorageFirstLayer() {
        let ajaxTimeOut = $.ajax({
            url: "/tablegroupview/menu/0",
            type: "GET",
            dataType: "json",
            timeout: 2000,
            success: function (data) {
                console.log('成功获取第一层层级关系');
                this.setState({ treeData: data['data'] });  // 将第一层级数据赋值给状态机
            }.bind(this),
            error: function (xhr, status, err) {
            },
            complete: function (XMLHttpRequest, status) {  // 请求完成后最终执行参数
                if (status === 'timeout') {  // 超时,status,success,error等值的情况
                    ajaxTimeOut.abort();  // 取消请求
                    console.log('网络不稳定');
                }
            }
        });

    }
    // 通过id获取下一层层级关系
    getKnowledgeStorageNextLayer(knowid) {
        return new Promise((resolve) => {
            let ajaxTimeOut = $.ajax({
                url: "/tablegroupview/menu/" + knowid,
                type: "GET",
                dataType: "json",
                timeout: 2000,
                success: function (data) {
                    if (data.errorCode === 1) {
                    }
                    else {
                        this.setState({ TreeNodeData: data['data'] }); //将下一层级菜单内容赋值给状态机
                    }
                }.bind(this),
                error: function (xhr, status, err) {
                },
                complete: function (XMLHttpRequest, status) { //请求完成后最终执行参数
                    if (status === 'timeout') {  //超时,status,success,error等值的情况
                        ajaxTimeOut.abort(); //取消请求
                    }
                }
            });
        })
    }

    getKnowInfo(knowid=1) {
        let ajaxTimeOut = $.ajax({
            url: "/tablegroupview/tables/" + knowid,
            type: "GET",
            dataType: "json",
            timeout: 2000,
            success: function(data) {
                this.setState({ infos: data});  // 将ajax返回的详细数据传到state中
            }.bind(this),
            error: function (xhr, status, err) {
            },
            complete: function (XMLHttpRequest, status) {
                            if (status === 'timeout') {
                                ajaxTimeOut.abort();
                            }
                        }
        })
    }

    renderTreeNodes(data) {
        return data.map((item) => {
            if (item.children) {
                return (
                    <TreeNode title={item.name} key={item.id} dataRef={item}>
                        {this.renderTreeNodes(item.children)}
                    </TreeNode>
                );
            }
            return <TreeNode key={item.id} title={item.name} dataRef={item} />;
        });
    }

    componentDidMount() {
        this.getKnowledgeStorageFirstLayer(); //获取第一层级菜单内容
        this.getKnowInfo();
    }

    onLoadData(treeNode) {
        return new Promise((resolve) => {
            this.getKnowledgeStorageNextLayer(treeNode.props.eventKey);
            setTimeout(() => {
                treeNode.props.dataRef.children = [
                    /*根据id设置子节点 数据格式:{ title: '数学', key: `${treeNode.props.eventKey}-0` }*/
                    ...this.state.TreeNodeData
                ];
                this.setState({
                    treeData: [...this.state.treeData],
                    info: [...this.state.infos]
                });
                console.log(this.state);
                resolve();
            }, 1000);
        });
    };

    onSelect(expandedKeys,e) {
        this.getKnowInfo(expandedKeys);
        this.setState({ title: e.selectedNodes[0].props.title })
    };


    renderTreeNodes(data) {
        return data.map((item) => {
            if (item.children) {
                return (
                    <TreeNode title={ item.name } key={ item.id } dataRef={ item }>
                        {this.renderTreeNodes(item.children)}
                    </TreeNode>
                );
            }
            return <TreeNode title={ item.name } key={ item.id } dataRef={ item } />;
        });
    };

    render() {
        return (
            <div className="container">
                <div className="row">
                    <div className="col-lg-2 col-md-2 container">
                        <div className="panel panel-primary">
                            <div className="panel-heading">
                                <h4 className="panel-title">数据集分类</h4>
                            </div>
                            <div className="list-group">
                                <Tree loadData={ this.onLoadData } onSelect={ this.onSelect }>
                                    { this.renderTreeNodes(this.state.treeData) }
                                </Tree>
                            </div>
                        </div>
                    </div>
                    <Info infos={ this.state.infos } title={ this.state.title } />
                </div>
            </div>
                );
            }
}
